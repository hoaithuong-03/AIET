import logging
import os
from pathlib import Path
from typing import Optional
import asyncio

import chromadb
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.gemini import Gemini
from app.rag.tools import crawl_and_index_story

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

class StoryChatService:
    def __init__(self, persist_dir: str = "storage/chroma_db"):
        self.persist_dir = Path(persist_dir)
        
        # Configure Settings
        logger.info("Initializing Local Embedding Model...")
        Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-small")
        
        # Configure Gemini LLM
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if google_api_key:
            logger.info("Initializing Gemini Flash Latest LLM...")
            Settings.llm = Gemini(
                model_name="models/gemini-flash-latest",
                api_key=google_api_key
            )
        else:
            logger.error("GOOGLE_API_KEY not found in environment.")
            raise ValueError("GOOGLE_API_KEY is required for ChatService.")
        
        # Initialize Vector Store
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.chroma_collection = self.chroma_client.get_or_create_collection("stories")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        
        # Load Index
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)
        
        # Initialize Query Engine
        # We use a simple query engine to save API quota and ensure stability
        self.query_engine = self.index.as_query_engine(
            llm=Settings.llm,
            similarity_top_k=3,
            response_mode="compact" # Optimize for speed and quota
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ResourceExhausted),
        reraise=True
    )
    async def _call_engine(self, query: str):
        # QueryEngine.query is a synchronous call but we run it in a thread or just call it
        # Since this is a simple call, we can use aioquery if available or just direct call
        response = self.query_engine.query(query)
        return str(response)

    async def ask(self, query: str) -> str:
        """Asynchronous query handling with retry logic for API limits."""
        try:
            result = await asyncio.to_thread(self.query_engine.query, query)
            return str(result)
        except ResourceExhausted as e:
            logger.error(f"Quota exceeded: {e}")
            return f"Hệ thống AI đang tạm thời quá tải hoặc hết hạn mức (Quota Exceeded). Lỗi chi tiết: {e}"
        except Exception as e:
            logger.error(f"Production error in ChatService: {e}")
            return f"Xin lỗi, Agent gặp lỗi khi xử lý câu hỏi: {str(e)}"


if __name__ == "__main__":
    # Test (internal)
    import asyncio
    import traceback
    async def main():
        try:
            service = StoryChatService()
            response = await service.ask("Thiết Trụ là ai?")
            print(f"AI Response: {response}")
        except Exception:
            traceback.print_exc()
            
    asyncio.run(main())


