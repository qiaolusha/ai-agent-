import time
from openai import OpenAI
from .settings import settings


def get_client() -> OpenAI:
    # SDK 默认也会读环境变量 OPENAI_API_KEY
    # 这里显式传入，方便你后续换 base_url / proxy 等
    return OpenAI(api_key=settings.openai_api_key)


def chat_once(message: str, system: str | None = None) -> tuple[str, int, str | None]:
    """
    最小闭环：Responses API -> output_text
    """
    client = get_client()
    start = time.perf_counter()

    input_items = []
    if system:
        input_items.append({"role": "system", "content": system})
    input_items.append({"role": "user", "content": message})

    resp = client.with_options(timeout=settings.request_timeout_s).responses.create(
        model=settings.openai_model,
        input=input_items,
    )

    latency_ms = int((time.perf_counter() - start) * 1000)
    request_id = getattr(resp, "_request_id", None)  # SDK 支持 request id 便于排查 <!--citation:1-->
    return resp.output_text or "", latency_ms, request_id


def parse_structured(message: str, text_format) -> tuple[object, int, str | None]:
    """
    Structured Outputs：responses.parse + text_format=PydanticModel
    """
    client = get_client()
    start = time.perf_counter()

    resp = client.with_options(timeout=settings.request_timeout_s).responses.parse(
        model=settings.openai_structured_model,
        input=[
            {"role": "system", "content": "Return only data that matches the given schema."},
            {"role": "user", "content": message},
        ],
        text_format=text_format,
    )

    latency_ms = int((time.perf_counter() - start) * 1000)
    request_id = getattr(resp, "_request_id", None)
    return resp.output_parsed, latency_ms, request_id
