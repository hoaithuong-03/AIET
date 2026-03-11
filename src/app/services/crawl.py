import time
import asyncio
import json
import csv
import os
import re
from bs4 import BeautifulSoup
from app.utils.http_client import fetch_page
from app.schemas.story import StoryDetail, ChapterInfo, ChapterContent

class CrawlerService:
    @staticmethod
    async def fetch_and_parse(url: str) -> tuple[BeautifulSoup | None, int]:
        """Fetch page and return BeautifulSoup object."""
        html, status_code = await fetch_page(url)
        if status_code != 200:
            return None, status_code
        return BeautifulSoup(html, "html.parser"), 200

    @staticmethod
    def parse_story_info(soup: BeautifulSoup, url: str) -> StoryDetail:
        """Parse story details from the main story page."""
        title = soup.select_one("h3.title").get_text(strip=True) if soup.select_one("h3.title") else "Unknown"
        
        desc_elem = soup.select_one(".desc-text")
        description = desc_elem.get_text(strip=True) if desc_elem else ""

        author_elem = soup.select_one(".info a[itemprop='author']")
        author = author_elem.get_text(strip=True) if author_elem else "Unknown"

        status_elem = soup.select_one(".info .text-success") or soup.select_one(".info .text-primary")
        status = status_elem.get_text(strip=True) if status_elem else "Unknown"

        categories = [a.get_text(strip=True) for a in soup.select(".info a[itemprop='genre']")]
        
        # Extract slug from URL or title
        slug = url.strip("/").split("/")[-1]

        # Basic chapter list from first page
        chapters = CrawlerService.parse_chapter_list(soup)

        return StoryDetail(
            title=title,
            description=description,
            author=author,
            status=status,
            categories=categories,
            source_url=url,
            slug=slug,
            total_chapters=len(chapters), # Initial count, updated later if pagination used
            chapters=chapters
        )

    @staticmethod
    def parse_chapter_list(soup: BeautifulSoup) -> list[ChapterInfo]:
        """Parse list of chapters from a page."""
        chapters = []
        chapter_list = soup.select("#list-chapter .row .list-chapter li a")
        for link in chapter_list:
            title = link.get("title", link.get_text(strip=True))
            url = link.get("href")
            
            # Extract chapter number from title
            number = 0
            match = re.search(r'Chương\s+(\d+)', title, re.IGNORECASE)
            if match:
                number = int(match.group(1))
            
            chapters.append(ChapterInfo(number=number, title=title, url=url))
        return chapters

    @staticmethod
    def get_total_pages(soup: BeautifulSoup) -> int:
        """Extract total number of pagination pages."""
        pagination = soup.select(".pagination li a")
        if not pagination:
            return 1
        
        last_page_url = pagination[-2]["href"] if len(pagination) >= 2 else None # usually Last is the second to last item '>>'
        if last_page_url:
            # extract page number from url e.g. /page-5/
            try:
                part = last_page_url.strip("/").split("trang-")[-1]
                return int(part)
            except:
                return 1
        return 1

    @staticmethod
    async def crawl_chapters_pagination(base_url: str, start_page: int, total_pages: int) -> list[ChapterInfo]:
        """Crawl all chapter pages."""
        all_chapters = []
        # Concurrency could be added here with gather, but let's be polite first with sequential or limited batch
        
        for page in range(start_page + 1, total_pages + 1):
            page_url = f"{base_url}trang-{page}/"
            soup, status = await CrawlerService.fetch_and_parse(page_url)
            if soup:
                chapters = CrawlerService.parse_chapter_list(soup)
                all_chapters.extend(chapters)
            await asyncio.sleep(0.5) # polite delay
            
        return all_chapters

    @staticmethod
    async def crawl_url(url: str) -> dict:
        """Crawl the given URL and return the response data."""
        start_time = time.perf_counter()
        try:
            soup, status_code = await CrawlerService.fetch_and_parse(url)
            if status_code != 200:
                duration = int((time.perf_counter() - start_time) * 1000)
                return {
                    "success": False, 
                    "url": url, 
                    "content_type": "unknown", 
                    "error": f"HTTP {status_code}", 
                    "crawl_time_ms": duration
                }
            
            if soup.select_one("#list-chapter"):
                story = CrawlerService.parse_story_info(soup, url)
                
                # Handle Pagination
                total_pages = CrawlerService.get_total_pages(soup)
                if total_pages > 1:
                    additional_chapters = await CrawlerService.crawl_chapters_pagination(url, 1, total_pages)
                    story.chapters.extend(additional_chapters)
                
                story.total_chapters = len(story.chapters)

                # Remove re-indexing, rely on parse_chapter_list regex

                return {
                    "success": True,
                    "url": url,
                    "content_type": "story",
                    "data": story.model_dump(),
                    "error": None,
                    "crawl_time_ms": int((time.perf_counter() - start_time) * 1000),
                }

            elif soup.select_one(".chapter-c"):
                 # ... same
                story_title = soup.select_one(".truyen-title").get_text(strip=True)
                chapter_title = soup.select_one(".chapter-title").get_text(strip=True)
                content_html = soup.select_one(".chapter-c").decode_contents()
                content_text = soup.select_one(".chapter-c").get_text("\n", strip=True)

                return {
                    "success": True,
                    "url": url,
                    "content_type": "chapter",
                    "data": {
                        "story_title": story_title,
                        "title": chapter_title,
                        "content_text": content_text,
                        "content_html": content_html
                    },
                     "error": None,
                    "crawl_time_ms": int((time.perf_counter() - start_time) * 1000),
                }
            
            else:
                 return {
                    "success": False,
                    "url": url,
                    "content_type": "unknown",
                    "error": "Unknown page structure",
                    "crawl_time_ms": int((time.perf_counter() - start_time) * 1000),
                }

        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e),
                "crawl_time_ms": int((time.perf_counter() - start_time) * 1000),
            }

    @staticmethod
    def save_to_file(data: dict, format: str = "json", filename: str = "crawled_data"):
        """Save crawled data to file."""
        if format == "json":
            with open(f"{filename}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        elif format == "csv":
            # Basic CSV flattened structure implementation
            # This is complex for nested structures like Story, keeping it simple for now
            pass

    @staticmethod
    async def crawl_full_story(url: str, output_dir: str = "crawled_stories", limit: int | None = None) -> dict:
        """
        Crawl everything about a story: metadata and all chapters.
        Saves to {output_dir}/{story_slug}/
          - metadata.json
          - chapter_1.txt
          - chapter_2.txt
          ...
        """
        start_time = time.perf_counter()
        
        # 1. Fetch Story Info
        soup, status = await CrawlerService.fetch_and_parse(url)
        if not soup:
            return {"success": False, "error": f"Failed to fetch story info: {status}"}
        
        if not soup.select_one("#list-chapter"):
             return {"success": False, "error": "URL does not look like a story main page"}

        story = CrawlerService.parse_story_info(soup, url)
        
        # 2. Prepare Output Directory
        story_dir = os.path.join(output_dir, story.slug)
        os.makedirs(story_dir, exist_ok=True)
        
        # 3. Save Metadata
        metadata_path = os.path.join(story_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(story.model_dump(), f, ensure_ascii=False, indent=4)
            
        # 4. Get All Chapter URLs (handling pagination)
        # First page chapters are already in story.chapters
        all_chapters = story.chapters
        
        total_pages = CrawlerService.get_total_pages(soup)
        if total_pages > 1:
            more_chapters = await CrawlerService.crawl_chapters_pagination(url, 1, total_pages)
            all_chapters.extend(more_chapters)
            
        # Deduplication just in case
        seen_urls = set()
        unique_chapters = []
        for chap in all_chapters:
            if chap.url not in seen_urls:
                unique_chapters.append(chap)
                seen_urls.add(chap.url)
        
        # Sort by chapter number to ensure strict order (1, 2, 3...)
        unique_chapters.sort(key=lambda x: x.number)
        
        # Apply limit
        if limit and limit > 0:
            unique_chapters = unique_chapters[:limit]
            
        downloaded_count = 0
        errors = []

        # 5. Download Each Chapter Content
        for chap in unique_chapters:
            try:
                # Assuming chapter numbers are correct, or use index
                # Number parsing was done in parse_chapter_list
                chap_num = chap.number if chap.number > 0 else (unique_chapters.index(chap) + 1)
                
                c_soup, c_status = await CrawlerService.fetch_and_parse(chap.url)
                if c_status == 200 and c_soup:
                    content_elem = c_soup.select_one(".chapter-c")
                    if content_elem:
                        # Save content
                        content_text = content_elem.get_text("\n", strip=True)
                        
                        chapter_data = {
                            "title": chap.title,
                            "content": content_text,
                            "url": chap.url
                        }
                        
                        file_name = f"chapter{chap_num}.json"
                        file_path = os.path.join(story_dir, file_name)
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(chapter_data, f, ensure_ascii=False, indent=4)
                        
                        downloaded_count += 1
                else:
                    errors.append(f"Failed to fetch chapter {chap_num}: {c_status}")
                
            except Exception as e:
                errors.append(f"Error chapter {chap.title}: {str(e)}")
            
            # Polite delay
            await asyncio.sleep(0.5)

        return {
            "success": True,
            "story_title": story.title,
            "output_dir": story_dir,
            "total_chapters_found": len(all_chapters),
            "chapters_downloaded": downloaded_count,
            "limit_applied": limit,
            "errors": errors,
            "total_time_ms": int((time.perf_counter() - start_time) * 1000)
        }

            
        