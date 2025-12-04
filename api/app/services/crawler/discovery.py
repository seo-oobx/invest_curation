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

    def extract_event_date(self, text: str) -> Optional[str]:
        """
        Extract potential event date from text.
        Returns ISO format date string (YYYY-MM-DD) or None.
        """
        import re
        from datetime import date
        
        current_year = date.today().year
        
        # Korean pattern: 12월 5일, 1월, 내년 상반기 등
        # Simple pattern: (\d+)월 (\d+)일
        match = re.search(r"(\d{1,2})월\s*(\d{1,2})일", text)
        if match:
            month, day = map(int, match.groups())
            # Simple logic: if month < current month, assume next year? 
            # Or just assume current year for now.
            # If today is Dec and we find Jan, it's next year.
            year = current_year
            if month < date.today().month:
                year += 1
            try:
                return date(year, month, day).isoformat()
            except:
                pass
                
        # English pattern: Jan 15, January 15th
        eng_months = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        match = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})", text, re.IGNORECASE)
        if match:
            month_str, day_str = match.groups()
            month = eng_months[month_str.lower()[:3]]
            day = int(day_str)
            year = current_year
            if month < date.today().month:
                year += 1
            try:
                return date(year, month, day).isoformat()
            except:
                pass
        
        return None

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
                    
                    # Try to extract event date from title or description
                    target_date = self.extract_event_date(title)
                    if not target_date:
                        target_date = self.extract_event_date(description)
                    
                    # If no date found, default to 3 months from now (as per user request 2-6 months)
                    # But mark it as unconfirmed?
                    # For now, let's just use a default if not found, so we populate the DB.
                    if not target_date:
                        # Default: 3 months later
                        from datetime import date, timedelta
                        target_date = (date.today() + timedelta(days=90)).isoformat()

                    discovered_events.append({
                        "type": "DISCOVERY",
                        "ticker": self.ticker,
                        "title": title,
                        "description": description, 
                        "source_url": link,
                        "crawled_at": datetime.now().isoformat(),
                        "pub_date": pub_date,
                        "target_date": target_date
                    })
                    
        except Exception as e:
            print(f"Error fetching RSS for {self.ticker}: {e}")
            
        return discovered_events

    # Unused methods from BaseCrawler
    async def crawl(self, browser):
        pass

    def parse(self, html_content: str) -> Optional[Dict[str, Any]]:
        pass
