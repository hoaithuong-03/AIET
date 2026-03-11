import logging
from app.services.crawl import CrawlerService
from app.rag.ingest import StoryIngestionService
import asyncio

logger = logging.getLogger(__name__)

async def crawl_and_index_story(url: str, limit: int = 50) -> str:
    """
    Crawl a story from TruyenFull and automatically index it into the AI's memory.
    Args:
        url: The main URL of the story (e.g., https://truyenfull.vision/tien-nghich/)
        limit: Number of chapters to download (default is 50 for speed).
    """
    logger.info(f"Tool called: crawl_and_index_story for {url}")
    
    try:
        # 1. Crawl
        crawler = CrawlerService()
        result = await crawler.crawl_full_story(url, limit=limit)
        
        if not result.get("success"):
            return f"Lỗi khi crawl: {result.get('error')}"
        
        # 2. Ingest/Index automatically
        ingest_service = StoryIngestionService()
        ingest_service.build_index()
        
        return (
            f"Thành công! Đã tải xong truyện '{result['story_title']}' "
            f"với {result['chapters_downloaded']} chương. "
            f"Dữ liệu đã được nạp vào bộ nhớ AI, bạn có thể hỏi về truyện này ngay bây giờ."
        )
        
    except Exception as e:
        logger.error(f"Error in crawl_and_index_story tool: {e}")
        return f"Có lỗi xảy ra trong quá trình xử lý: {str(e)}"

# Wrapper for synchronous tool call if needed by some agent types
def sync_crawl_and_index_story(url: str, limit: int = 50) -> str:
    return asyncio.run(crawl_and_index_story(url, limit))
