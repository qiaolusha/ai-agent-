import time
from openai import OpenAI
from .settings import settings
from .tools import TOOLS, run_tool
from .llm import get_client


def run_agent(message: str) -> tuple[str, list[dict], int, str | None]:
    """
    按官方 tool-calling flow：
    1) 带 tools 调 responses.create
    2) 收到 function_call 就执行
    3) 追加 function_call_output 再发一次
    循环最多 MAX_TOOL_ITERS 次
    """
    client: OpenAI = get_client()
    start = time.perf_counter()

    input_list = [{"role": "user", "content": message}]
    tool_calls_log: list[dict] = []

    for _ in range(settings.max_tool_iters):
        resp = client.with_options(timeout=settings.request_timeout_s).responses.create(
            model=settings.openai_model,
            tools=TOOLS,
            input=input_list,
        )

        # 把模型输出保存进 input_list，作为下一轮上下文（官方示例也是这么做） <!--citation:4-->
        input_list += resp.output

        calls = [item for item in resp.output if getattr(item, "type", None) == "function_call"]
        if not calls:
            latency_ms = int((time.perf_counter() - start) * 1000)
            request_id = getattr(resp, "_request_id", None)
            return resp.output_text or "", tool_calls_log, latency_ms, request_id

        for item in calls:
            name = item.name
            arguments = item.arguments
            call_id = item.call_id

            tool_calls_log.append({"name": name, "arguments": arguments, "call_id": call_id})

            output_str = run_tool(name=name, arguments_json=arguments, files_dir=settings.files_dir)
            input_list.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": output_str,
                }
            )

    latency_ms = int((time.perf_counter() - start) * 1000)
    return "Reached max tool iterations; please refine the question.", tool_calls_log, latency_ms, None
