from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.crawl import CrawlRequest, CrawlResponse
from app.services.crawl import CrawlerService

from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/crawl", tags=["Crawl"])

class FullCrawlRequest(BaseModel):
    url: str
    limit: Optional[int] = 50

@router.post("/crawl")
async def crawl_url(request: CrawlRequest) -> CrawlResponse:
    """Endpoint to crawl a given URL for metadata or single chapter."""
    result = await CrawlerService.crawl_url(request.url)
    return CrawlResponse(**result)

from app.rag.tools import crawl_and_index_story

@router.post("/full")
async def crawl_full_story(request: FullCrawlRequest):
    """Endpoint to download an entire story and save to disk + Auto Index."""
    # Use the tool-version which handles both crawling and indexing
    result_text = await crawl_and_index_story(request.url, limit=request.limit or 50)
    
    # Check for success in the returned string (or we could refactor tools to return dict)
    if "Thành công" in result_text:
        return {"success": True, "message": result_text}
    else:
        return {"success": False, "error": result_text}
    