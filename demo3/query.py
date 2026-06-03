"""
RAG 查询模块：检索 → 生成回答 → 返回带引用的结构化结果
"""
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.response.schema import Response
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.postgres import PGVectorStore
from config import *

Settings.embed_model = OpenAIEmbedding(model=EMBED_MODEL, api_key=OPENAI_API_KEY)
Settings.llm = OpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY)


def get_index() -> VectorStoreIndex:
    vector_store = PGVectorStore.from_params(
        database="ragdb", host="localhost",
        password="ragpass", port=5432, user="raguser",
        table_name="rag_docs", embed_dim=1536,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store, storage_context=storage_context
    )


def parse_citations(response: Response) -> list[dict]:
    """
    从 source_nodes 中提取引用信息
    每条引用包含: chunk_id / file_name / page / score / 文本片段
    """
    citations = []
    for node in response.source_nodes:
        meta = node.node.metadata
        citations.append({
            "chunk_id":  node.node.node_id,
            "file_name": meta.get("file_name", "unknown"),
            "page":      meta.get("page_label", "?"),
            "score":     round(node.score or 0.0, 4),
            "snippet":   node.node.text[:200] + "..."  # 显示前200字符
        })
    return citations


def rag_query(question: str) -> dict:
    """
    主查询函数，返回:
    {
        "answer": str,
        "citations": [{"chunk_id", "file_name", "page", "score", "snippet"}],
        "contexts": [str]  # 供 RAGAS 评估使用
    }
    """
    index = get_index()

    # TOP_K=5: 检索5个最相关的 chunk
    # 取舍: 太小→漏关键信息；太大→LLM上下文过长成本高
    query_engine = index.as_query_engine(
        similarity_top_k=TOP_K,
        # 可选：开启 rerank（需要 Cohere API key）
        # node_postprocessors=[CohereRerank(api_key=COHERE_KEY, top_n=3)]
    )

    response = query_engine.query(question)
    citations = parse_citations(response)
    contexts = [node.node.text for node in response.source_nodes]

    return {
        "answer": str(response),
        "citations": citations,
        "contexts": contexts,
    }


if __name__ == "__main__":
    q = "文档的主要内容是什么？"
    result = rag_query(q)
    print(f"\n回答：{result['answer']}\n")
    print("引用来源：")
    for c in result["citations"]:
        print(f"  [{c['file_name']} p.{c['page']}] score={c['score']}  chunk_id={c['chunk_id'][:8]}...")
        print(f"  片段: {c['snippet']}\n")
