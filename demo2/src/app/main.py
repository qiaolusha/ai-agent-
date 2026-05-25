import time
import logging
from collections.abc import Iterable

from fastapi import FastAPI, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent

# 导入数据格式模板（入参/出参规矩）
from .schemas import ChatRequest, ChatResponse, InterviewPlan, AgentRequest, AgentResponse
# 导入AI基础调用函数
from .llm import chat_once, parse_structured, get_client
# 导入AI智能体核心函数
from .agent import run_agent
# 导入配置管家
from .settings import settings

log = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="LLM FastAPI Starter", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        answer, latency_ms, request_id = chat_once(req.message, system=req.system)
        return ChatResponse(
            answer=answer,
            model=settings.openai_model,
            latency_ms=latency_ms,
            request_id=request_id,
        )
    except Exception as e:
        log.exception("chat failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/plan", response_model=InterviewPlan)
def plan(req: ChatRequest):
    """
    Structured Outputs demo：返回严格符合 InterviewPlan schema 的 JSON
    """
    prompt = f"""
你是一个严谨的规划助手。请给出一个可执行的面试冲刺计划。
背景：我会 Java 后端，有一点 Python，现在想用 Python 做 AI Agent 开发找实习。
请输出一个 14 天计划（duration_days=14），每天给 focus + 3-6 条 tasks。
""".strip()

    try:
        parsed, latency_ms, request_id = parse_structured(
            message=prompt + "\n\n用户补充信息：" + req.message,
            text_format=InterviewPlan,
        )
        # 这里 parsed 已经是 InterviewPlan 实例（Pydantic model），FastAPI 会自动序列化
        log.info("plan ok latency_ms=%s request_id=%s", latency_ms, request_id)
        return parsed
    except Exception as e:
        log.exception("plan failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    try:
        answer, tool_calls, latency_ms, request_id = run_agent(req.message)
        return AgentResponse(
            answer=answer,
            tool_calls=tool_calls,
            model=settings.openai_model,
            latency_ms=latency_ms,
            request_id=request_id,
        )
    except Exception as e:
        log.exception("agent failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/stream", response_class=EventSourceResponse)
def chat_stream(req: ChatRequest) -> Iterable[ServerSentEvent]:
    """
    SSE：把 OpenAI streaming events 转发给客户端
    只做纯文本流式（不混 tools），先把“能流起来”搞定。
    """
    client = get_client()

    input_items = []
    if req.system:
        input_items.append({"role": "system", "content": req.system})
    input_items.append({"role": "user", "content": req.message})

    start = time.perf_counter()

    # OpenAI：stream=True 会返回一串事件（语义化 event types） <!--citation:5-->
    stream = client.with_options(timeout=settings.request_timeout_s).responses.create(
        model=settings.openai_model,
        input=input_items,
        stream=True,
    )

    yield ServerSentEvent(comment="stream start")

    try:
        for event in stream:
            etype = getattr(event, "type", "")
            # 文本增量事件：response.output_text.delta；事件对象上会有 delta 字段 <!--citation:6-->
            if etype == "response.output_text.delta":
                delta = getattr(event, "delta", "")
                if delta:
                    yield ServerSentEvent(raw_data=delta, event="token")
            elif etype == "response.completed":
                break

        latency_ms = int((time.perf_counter() - start) * 1000)
        yield ServerSentEvent(raw_data=f"\n[DONE] latency_ms={latency_ms}", event="done")
    except Exception as e:
        yield ServerSentEvent(raw_data=f"[ERROR] {e}", event="error")
