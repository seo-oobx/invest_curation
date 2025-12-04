from typing import List, Dict, Any, Optional
from app.services.crawler.base import BaseCrawler
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote

class EventDiscoveryCrawler(BaseCrawler):
    """
    Event Discovery Crawler (RSS Version)
    
    목표: 특정 종목(키워드)과 관련된 미래 이벤트(일정)를 발견합니다.
    방법: Google News RSS를 통해 '일정', '출시', '발표', '공개' 등의 키워드와 조합하여 검색.
    장점: 브라우저 없이 빠르고 안정적으로 데이터 수집 가능.
    """
    
    def __init__(self, ticker: str, headless: bool = True):
        super().__init__(headless)
        self.ticker = ticker
        # 검색 쿼리 조합: "{종목명} 일정 OR 출시 OR 발표 OR 공개"
        self.search_query = f"{ticker} 일정 OR 출시 OR 발표 OR 공개"
        encoded_query = quote(self.search_query)
        # Google News RSS URL (Korean, Korea region)
        self.rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"

    async def run(self) -> List[Dict[str, Any]]:
        """
        Override run method to use RSS instead of Playwright.
        """
        print(f"Fetching RSS for {self.ticker}...")
        discovered_events = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.rss_url, timeout=10.0)
                
                if response.status_code != 200:
                    print(f"Failed to fetch RSS for {self.ticker}: {response.status_code}")
                    return []
                
                # Parse XML
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                # Limit to top 10 items
                for item in items[:10]:
                    title = item.find("title").text if item.find("title") is not None else "No Title"
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    description = item.find("description").text if item.find("description") is not None else ""
                    
                    # Clean title (remove source at the end, e.g. " - 뉴스1")
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                    
                    discovered_events.append({
                        "type": "DISCOVERY",
                        "ticker": self.ticker,
                        "title": title,
                        "description": description, # RSS description is often short or HTML
                        "source_url": link,
                        "crawled_at": datetime.now().isoformat(),
                        "pub_date": pub_date
                    })
                    
        except Exception as e:
            print(f"Error fetching RSS for {self.ticker}: {e}")
            
        return discovered_events

    # Unused methods from BaseCrawler
    async def crawl(self, browser):
        pass

    def parse(self, html_content: str) -> Optional[Dict[str, Any]]:
        pass
