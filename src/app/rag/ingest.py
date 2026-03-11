import os
import json
import logging
from pathlib import Path
from typing import List

from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class StoryIngestionService:
    def __init__(self, data_dir: str = "crawled_stories", persist_dir: str = "storage/chroma_db"):
        self.data_dir = Path(data_dir)
        self.persist_dir = Path(persist_dir)
        
        # Configure Settings to use Local Embeddings
        logger.info("Initializing Local Embedding Model (intfloat/multilingual-e5-small)...")
        Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-small")
        
        # Initialize Vector Store (Chroma)
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.chroma_collection = self.chroma_client.get_or_create_collection("stories")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

    def load_documents(self) -> List[Document]:
        documents = []
        
        if not self.data_dir.exists():
            logger.error(f"Data directory {self.data_dir} does not exist.")
            return []

        # Iterate over each story directory
        for story_dir in self.data_dir.iterdir():
            if not story_dir.is_dir():
                continue
                
            metadata_path = story_dir / "metadata.json"
            if not metadata_path.exists():
                logger.warning(f"No metadata.json found in {story_dir}")
                continue
                
            # Read Metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                story_meta = json.load(f)
                
            story_title = story_meta.get("title", "Unknown")
            author = story_meta.get("author", "Unknown")
            logger.info(f"Processing story: {story_title}")

            # Read Chapters
            for chapter_file in story_dir.glob("chapter*.json"):
                try:
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        chap_data = json.load(f)
                        
                    content = chap_data.get("content", "")
                    chap_title = chap_data.get("title", "")
                    url = chap_data.get("url", "")
                    
                    if not content:
                        continue
                        
                    # Create Document
                    # We inject context into the text but also keep it in metadata
                    doc_text = f"Truyện: {story_title}\n{chap_title}\n\n{content}"
                    
                    doc = Document(
                        text=doc_text,
                        metadata={
                            "story_title": story_title,
                            "author": author,
                            "chapter_title": chap_title,
                            "url": url,
                            "filename": chapter_file.name
                        }
                    )
                    documents.append(doc)
                    
                except Exception as e:
                    logger.error(f"Error reading {chapter_file}: {e}")
                    
        logger.info(f"Loaded {len(documents)} documents.")
        return documents

    def build_index(self):
        docs = self.load_documents()
        if not docs:
            logger.info("No documents to index.")
            return

        logger.info("Building Vector Index (this might take a while)...")
        index = VectorStoreIndex.from_documents(
            docs, storage_context=self.storage_context, show_progress=True
        )
        logger.info("Index created and persisted successfully.")
        return index

if __name__ == "__main__":
    service = StoryIngestionService()
    service.build_index()
