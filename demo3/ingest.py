"""
文档摄入管道：PDF / Markdown / 纯文本 → pgvector
"""
import pymupdf4llm
from pathlib import Path
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.postgres import PGVectorStore
import sqlalchemy
from config import *


# ── 1. 全局 Settings ───────────────────────────────────────────────────────────
Settings.embed_model = OpenAIEmbedding(
    model=EMBED_MODEL, api_key=OPENAI_API_KEY
)
Settings.llm = OpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY)


# ── 2. 初始化 pgvector ─────────────────────────────────────────────────────────
def get_vector_store(table_name: str = "rag_docs") -> PGVectorStore:
    engine = sqlalchemy.create_engine(DB_URL)
    # 确保 vector 扩展存在
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    return PGVectorStore.from_params(
        database="ragdb",
        host="localhost",
        password="ragpass",
        port=5432,
        user="raguser",
        table_name=table_name,
        embed_dim=1536,    # text-embedding-3-small 的维度
    )


# ── 3. 文档解析 ────────────────────────────────────────────────────────────────
def load_document(file_path: str) -> list[Document]:
    """
    支持 PDF / Markdown / txt
    返回带 metadata 的 Document 列表
    """
    path = Path(file_path)
    file_name = path.name

    if path.suffix.lower() == ".pdf":
        # pymupdf4llm: 输出带页码的 Markdown，保留结构
        md_text = pymupdf4llm.to_markdown(str(path), page_chunks=True)
        docs = []
        for i, page in enumerate(md_text):
            docs.append(Document(
                text=page["text"],
                metadata={
                    "file_name": file_name,
                    "page_label": str(page.get("page", i + 1)),
                    "source": str(path),
                }
            ))
        return docs

    elif path.suffix.lower() in [".md", ".txt"]:
        text = path.read_text(encoding="utf-8")
        return [Document(
            text=text,
            metadata={"file_name": file_name, "page_label": "1", "source": str(path)}
        )]

    else:
        raise ValueError(f"不支持的文件类型: {path.suffix}")


# ── 4. 主入库函数 ──────────────────────────────────────────────────────────────
def ingest(file_path: str) -> int:
    """
    完整 pipeline: 解析 → chunk → embed → 存入 pgvector
    返回写入的 node 数量
    """
    # 4.1 解析
    documents = load_document(file_path)
    print(f"[ingest] 解析完成，共 {len(documents)} 页/段落")

    # 4.2 Chunking
    # SentenceSplitter: 尊重句子边界，不会在句中截断
    # chunk_size=512 是经验起点：太小→碎片化；太大→噪音多、LLM 上下文压力大
    # chunk_overlap=50 防止边界处语义丢失
    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # 4.3 建索引（内部自动 embed + 写入向量库）
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True,
    )

    print(f"[ingest] 写入完成，文件: {file_path}")
    return len(documents)


if __name__ == "__main__":
    import sys
    ingest(sys.argv[1])
