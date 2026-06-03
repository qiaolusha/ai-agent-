# RAG 文档问答服务

一个基于 LlamaIndex + pgvector + FastAPI 的 RAG（检索增强生成）服务，支持文档上传、智能问答、引用来源追踪，以及 RAGAS 离线评估。

## 项目结构

```
demo4/
├── docker-compose.yml        # PostgreSQL + pgvector 容器
├── requirements.txt          # Python 依赖
├── config.py                 # 统一配置（模型、分块参数、数据库）
├── ingest.py                 # 文档解析 → 分块 → 向量化 → 入库
├── query.py                  # 检索 → 生成回答 → 返回引用
├── app.py                    # FastAPI HTTP 服务
├── evaluate.py               # RAGAS 离线评估脚本
├── data/                     # 存放待处理的文档（PDF/MD/TXT）
└── eval/
    └── qa_samples.json       # QA 测试样本
```

## 快速开始

### 1. 启动数据库

```bash
docker compose up -d
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

创建 `.env` 文件或在环境变量中设置：

```
OPENAI_API_KEY=sk-xxx
```

### 4. 文档入库

将文档放入 `data/` 目录，然后运行：

```bash
python ingest.py data/sample.pdf
```

支持格式：`.pdf`、`.md`、`.txt`

### 5. 测试查询

```bash
python query.py
```

### 6. 启动 API 服务

```bash
uvicorn app:app --reload --port 8000
```

API 端点：
- `POST /upload` — 上传文档并入库
- `POST /query` — 提问并获取带引用的回答
- `GET /health` — 健康检查

### 7. RAGAS 评估

准备 QA 样本（`eval/qa_samples.json`），然后运行：

```bash
python evaluate.py
```

输出四大指标：
- **faithfulness** — 忠实度（有无幻觉）
- **answer_relevancy** — 答案相关性
- **context_precision** — 检索精度
- **context_recall** — 检索召回

## 核心配置

在 [config.py](file:///f:/ZhuoMian/AgentCode/demo4/config.py) 中可调整关键参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_SIZE` | 512 | 文本分块大小（token数） |
| `CHUNK_OVERLAP` | 50 | 相邻分块重叠量 |
| `TOP_K` | 5 | 检索返回的相关文档数量 |

## 技术栈

- **框架**: LlamaIndex、FastAPI
- **向量数据库**: PostgreSQL + pgvector
- **LLM**: OpenAI (gpt-4o-mini)
- **Embedding**: OpenAI (text-embedding-3-small)
- **评估**: RAGAS
