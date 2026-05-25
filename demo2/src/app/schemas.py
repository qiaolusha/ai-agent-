from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    system: str | None = Field(default=None, max_length=4000)

class ChatResponse(BaseModel):
    answer: str
    model: str
    latency_ms: int
    request_id: str | None = None

# Structured Outputs：让模型输出严格符合 schema
class DailyTask(BaseModel):
    day: int = Field(..., ge=1, le=30)
    focus: str
    tasks: list[str]

class InterviewPlan(BaseModel):
    title: str
    target_role: str
    duration_days: int = Field(..., ge=1, le=60)
    daily: list[DailyTask]
    checkpoints: list[str]

class AgentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)

class AgentResponse(BaseModel):
    answer: str
    tool_calls: list[dict]
    model: str
    latency_ms: int
    request_id: str | None = None
