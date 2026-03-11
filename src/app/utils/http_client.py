import httpx
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings

# Initialize UserAgent object once
ua = UserAgent()

def get_random_headers() -> dict[str, str]:
    """Generate headers with a random User-Agent."""
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

async def create_http_client() -> httpx.AsyncClient:
    """Create and return an asynchronous HTTP client with random headers."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(settings.crawl_timeout_seconds),
        headers=get_random_headers(),
        follow_redirects=True,
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException, httpx.ConnectError))
)
async def fetch_page(url: str) -> tuple[str, int]:
    """Fetch a web page and return its status code and content with retries."""
    async with await create_http_client() as client:
        try:
            response = await client.get(url)
            response.raise_for_status() # Raise error for 4xx/5xx status codes to trigger retry if needed
            return response.text, response.status_code
        except httpx.HTTPStatusError as e:
            # Return content even on error if needed, or re-raise to retry
            # For this crawler, 404 might be valid end of pagination, so we might not want to retry 404 everywhere.
            # But generally for robustness, we return status.
            return e.response.text, e.response.status_code

    