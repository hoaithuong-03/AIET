from typing import Literal
from pydantic import BaseModel, Field

class CrawlRequest(BaseModel):
    """Schema for a crawl a single URL request."""
    url: str = Field(..., description="URL to crawl")

class CrawlResponse(BaseModel):
    """Response from crawl operation"""
    success: bool = Field(..., description="Indicates if the crawl was successful")
    url: str = Field(..., description="The URL that was crawled")
    content_type: Literal["story", "chapter", "unknown"] = Field(
        ..., description="Type of content identified at the URL"
    )
    data: dict | list | None = Field(default=None, description="Crawled data")
    error: str | None = Field(default=None, description="Error message if crawl failed")
    crawl_time_ms: int = Field(..., description="Time taken to crawl the URL in milliseconds")

class ErrorResponse(BaseModel):
    success: bool = False
    error: str = Field(..., description="Error message describing the failure")
    details: str | None = Field(default=None, description="Additional details about the error")