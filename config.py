import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Initializations kardiye
MODEL_NAME = "BAAI/bge-small-en"
QDRANT_URL = "http://localhost:6333"
PARENT_COLLECTION = "youtube_parents"
CHILD_COLLECTION = "youtube_children"
client = QdrantClient(url=QDRANT_URL)

embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)