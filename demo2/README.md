# LLM FastAPI Starter

一个基于 FastAPI + OpenAI SDK 的 AI 应用入门项目，适合初学者学习如何构建 AI Agent 服务。

## 项目简介

这是一个轻量级的 FastAPI 后端项目，演示了三种常见的 AI 应用场景：

1. **基础对话** - 调用大模型进行问答
2. **结构化输出** - 让 AI 输出严格符合格式的 JSON 数据
3. **AI Agent** - 让 AI 调用工具（查天气、搜索数据库、读取文件）完成任务

## 项目结构

```
src/app/
├── main.py        # 主入口：定义 API 路由
├── settings.py    # 配置管理：读取环境变量
├── schemas.py     # 数据模型：定义请求/响应格式
├── llm.py         # LLM 调用：封装 OpenAI API 调用
├── agent.py       # Agent 核心：工具调用循环
└── tools.py       # 工具实现：天气、搜索、文件读取
```

## 文件详解

### 1. settings.py - 配置管家

**作用**：集中管理所有配置项，从 `.env` 文件读取环境变量。

```python
class Settings(BaseSettings):
    openai_api_key: str | None = None      # OpenAI API 密钥
    openai_model: str = "gpt-5.2"          # 默认模型
    request_timeout_s: float = 30.0        # 请求超时时间
    max_tool_iters: int = 3                # Agent 最大工具调用次数
```

**为什么需要它**：避免硬编码密钥和配置，方便切换环境。

**使用方式**：在项目根目录创建 `.env` 文件：
```env
OPENAI_API_KEY=sk-your-key-here
```

---

### 2. schemas.py - 数据格式规矩

**作用**：用 Pydantic 定义请求和响应的数据格式，自动校验和序列化。

```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    system: str | None = Field(default=None, max_length=4000)
```

**为什么需要它**：
- 自动校验输入（如 `message` 不能为空）
- 自动生成 API 文档
- 自动将 Python 对象转为 JSON

---

### 3. llm.py - AI 基础调用

**作用**：封装 OpenAI API 的两种调用方式。

#### 函数 1：`chat_once()` - 普通对话
```python
def chat_once(message: str, system: str | None = None)
```
- 输入：用户消息 + 可选的系统提示
- 输出：AI 回复文本 + 耗时 + 请求 ID
- 用途：最简单的问答场景

#### 函数 2：`parse_structured()` - 结构化输出
```python
def parse_structured(message: str, text_format)
```
- 输入：提示词 + Pydantic 模型
- 输出：严格符合 schema 的 Python 对象
- 用途：让 AI 输出固定格式的数据（如计划表、配置等）

---

### 4. tools.py - 工具定义与实现

**作用**：定义 AI 可以调用的工具，以及工具的具体实现。

#### 三个工具：

| 工具名 | 功能 | 入参 |
|--------|------|------|
| `get_weather` | 查询天气 | `location`（地点） |
| `search_db` | 搜索知识库 | `query`（查询词） |
| `summarize_file` | 读取文件摘要 | `filename`（文件名） |

**工作流程**：
1. `TOOLS` 列表：告诉 AI 有哪些工具可用（JSON Schema 格式）
2. 工具函数：实际执行逻辑（目前用假数据，面试时可替换为真实 API）
3. `run_tool()`：统一入口，根据工具名分发调用

---

### 5. agent.py - AI Agent 核心

**作用**：实现工具调用循环（Tool Calling Loop）。

**工作流程**：
```
用户提问 → AI 判断是否需要工具 → 调用工具 → 拿到结果 → 继续回答
```

**核心逻辑**：
```python
for _ in range(max_tool_iters):  # 最多循环 3 次
    resp = client.responses.create(tools=TOOLS, input=input_list)
    
    # 如果 AI 调用了工具
    if function_call:
        执行工具 → 拿到结果 → 追加到 input_list
    else:
        返回最终答案
```

**为什么需要循环**：AI 可能需要多次调用工具才能完成任务（如先查天气，再搜索相关知识）。

---

### 6. main.py - API 路由入口

**作用**：定义 HTTP 接口，对外提供服务。

| 接口 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/v1/chat` | POST | 基础对话 |
| `/v1/plan` | POST | 生成结构化计划 |
| `/v1/agent` | POST | AI Agent（带工具调用） |
| `/v1/chat/stream` | POST | 流式对话（SSE） |

**示例：`/v1/chat` 接口**
```python
@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer, latency_ms, request_id = chat_once(req.message, system=req.system)
    return ChatResponse(answer=answer, ...)
```

