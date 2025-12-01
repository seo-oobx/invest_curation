from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page

class BaseCrawler(ABC):
    """
    Abstract Base Class for all crawlers.
    Enforces a standard interface for crawling and parsing data.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def run(self) -> List[Dict[str, Any]]:
        """
        Main execution method.
        Starts the browser, performs the crawl, and returns structured data.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            try:
                return await self.crawl(browser)
            finally:
                await browser.close()

    @abstractmethod
    async def crawl(self, browser: Browser) -> List[Dict[str, Any]]:
        """
        Implement the specific crawling logic here.
        Should return a list of dictionaries representing the crawled items.
        """
        pass

    @abstractmethod
    def parse(self, html_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse raw HTML content into structured data.
        """
        pass
