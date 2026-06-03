import os
from dotenv import load_dotenv

load_dotenv()

# LLM & Embedding
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# Chunking — 关键取舍参数，集中管理
CHUNK_SIZE = 512        # token 数。太小→碎片化丢上下文；太大→噪音多
CHUNK_OVERLAP = 50      # 相邻 chunk 重叠。防止边界语义断裂

# Retrieval
TOP_K = 5               # 检索数量。4~6 是经验平衡点

# pgvector
DB_URL = "postgresql+psycopg2://raguser:ragpass@localhost:5432/ragdb"
