from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseCrawler(ABC):
    """
    Abstract Base Class for all crawlers.
    Enforces a standard interface for crawling and parsing data.
    
    Note: This base class is now HTTP-based (using httpx) instead of browser-based.
    Subclasses should implement run() with their own HTTP logic.
    """
    
    def __init__(self, headless: bool = True):
        # headless parameter kept for backward compatibility but not used
        self.headless = headless

    @abstractmethod
    async def run(self) -> List[Dict[str, Any]]:
        """
        Main execution method.
        Should perform HTTP requests and return structured data.
        """
        pass

    def parse(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse raw content into structured data.
        Override in subclass if needed.
        """
        pass
