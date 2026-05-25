import json
import os
from pydantic import BaseModel, Field


# ---- 工具入参 schema（本地校验，防止模型胡填参数） ----
class GetWeatherArgs(BaseModel):
    location: str = Field(..., min_length=1, max_length=80)


class SearchDbArgs(BaseModel):
    query: str = Field(..., min_length=1, max_length=80)


class SummarizeFileArgs(BaseModel):
    filename: str = Field(..., min_length=1, max_length=120)


# ---- 工具定义（给模型看的 JSON Schema）----
TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a location. Use when user asks about weather.",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string", "description": "City, Country"}},
            "required": ["location"],
        },
    },
    {
        "type": "function",
        "name": "search_db",
        "description": "Search a tiny in-memory knowledge base for internship/interview related notes.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "summarize_file",
        "description": "Read a local text/markdown file from FILES_DIR and return its first N chars for summarization.",
        "parameters": {
            "type": "object",
            "properties": {"filename": {"type": "string"}},
            "required": ["filename"],
        },
    },
]


# ---- 工具实现（你本地执行） ----
_FAKE_DB = {
    "rag": "RAG=检索增强生成：chunk -> embedding -> vector search -> stuff into context -> answer with citations",
    "tool calling": "Tool calling/函数调用：模型产出 function_call(name,args,call_id)，你执行后回填 function_call_output(call_id,output)",
    "sse": "SSE=text/event-stream，用 yield 推送 token；FastAPI 0.135+ 提供 fastapi.sse.EventSourceResponse",
}


def get_weather(location: str) -> dict:
    args = GetWeatherArgs(location=location)
    # 这里先用假数据，面试时你可以说：真实项目会接天气 API，并做超时/缓存
    return {"location": args.location, "temp_c": 26, "condition": "Sunny"}


def search_db(query: str) -> dict:
    args = SearchDbArgs(query=query)
    q = args.query.strip().lower()
    hits = []
    for k, v in _FAKE_DB.items():
        if q in k or q in v.lower():
            hits.append({"key": k, "value": v})
    return {"query": args.query, "hits": hits[:5]}


def summarize_file(filename: str, files_dir: str) -> dict:
    args = SummarizeFileArgs(filename=filename)
    safe_name = os.path.basename(args.filename)  # 防目录穿越
    path = os.path.join(files_dir, safe_name)

    if not os.path.exists(path):
        return {"filename": safe_name, "error": "file_not_found"}

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    snippet = content[:1500]
    return {"filename": safe_name, "chars": len(content), "snippet": snippet}


def run_tool(name: str, arguments_json: str, files_dir: str) -> str:
    """
    返回字符串：作为 function_call_output.output 填回模型
    """
    args = json.loads(arguments_json or "{}")

    if name == "get_weather":
        result = get_weather(location=args.get("location", ""))
    elif name == "search_db":
        result = search_db(query=args.get("query", ""))
    elif name == "summarize_file":
        result = summarize_file(filename=args.get("filename", ""), files_dir=files_dir)
    else:
        result = {"error": "unknown_tool", "name": name}

    return json.dumps(result, ensure_ascii=False)
