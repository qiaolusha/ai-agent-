"""
RAG HTTP 服务
POST /upload  — 上传文档并入库
POST /query   — 提问并获取带引用的回答
"""
import shutil, tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from ingest import ingest
from query import rag_query

app = FastAPI(title="RAG 文档问答服务")

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


class QueryRequest(BaseModel):
    question: str


class Citation(BaseModel):
    chunk_id: str
    file_name: str
    page: str
    score: float
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传 PDF / Markdown / txt，解析并入向量库"""
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件类型: {suffix}，支持: {ALLOWED_EXTENSIONS}")

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        count = ingest(tmp_path)
        return {"status": "ok", "file": file.filename, "chunks_ingested": count}
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/query", response_model=QueryResponse)
async def query_document(req: QueryRequest):
    """提问，返回回答 + 引用来源"""
    if not req.question.strip():
        raise HTTPException(400, "问题不能为空")
    result = rag_query(req.question)
    return QueryResponse(
        answer=result["answer"],
        citations=[Citation(**c) for c in result["citations"]]
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
