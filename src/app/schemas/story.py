from pydantic import BaseModel, Field

class StoryBase(BaseModel):
    """Base schema for a story."""
    title: str = Field(..., description="Title of the story")
    description: str = Field(..., description="Description of the story")
    author: str | None = Field(default=None, description="Author of the story")
    status: str | None = Field(default=None, description="Status of the story")
    categories: list[str] = Field(default_factory=list, description="Categories of the story")
    source_url: str = Field(..., description="Source URL of the story")
    slug: str = Field(..., description="Slug for the story")
    total_chapters: int | None = Field(default=None, description="Total number of chapters")

class ChapterInfo(BaseModel):
    """Schema for chapter information."""
    number: int = Field(..., description="Chapter number")
    title: str = Field(..., description="Title of the chapter")
    url: str = Field(..., description="URL of the chapter")

class StoryDetail(StoryBase):
    """Detailed schema for a story including chapters."""
    chapters: list[ChapterInfo] = Field(default_factory=list, description="List of chapters in the story")

class ChapterContent(BaseModel):
    story_slug: str = Field(..., description="Slug of the story")
    story_title: str = Field(..., description="Title of the story")
    chapter_number: int = Field(..., description="Chapter number")
    title: str | None = Field(default=None, description="Title of the chapter")
    content: str = Field(..., description="Content of the chapter")
    source_url: str = Field(..., description="Source URL of the chapter")
    word_count: int | None = Field(default=None, description="Word count of the chapter")
