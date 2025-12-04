"""
Event Discovery Crawler (RSS Version)

목표: 특정 종목(키워드)과 관련된 **미래 예정 이벤트**를 발견합니다.
방법: Google News RSS를 통해 '예정', '계획', '출시 예정' 등 미래 지향적 키워드로 검색.
변경: GPT가 날짜를 추출하므로 여기서는 기본값 할당하지 않음.
"""

from typing import List, Dict, Any, Optional
from app.services.crawler.base import BaseCrawler
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote


class EventDiscoveryCrawler(BaseCrawler):
    """
    Event Discovery Crawler - Finds FUTURE events via RSS.
    """
    
    # Keywords that indicate FUTURE events (not past)
    FUTURE_KEYWORDS_KR = ["예정", "계획", "출시예정", "발표예정", "공개예정", "상반기", "하반기"]
    FUTURE_KEYWORDS_EN = ["upcoming", "scheduled", "expected", "planned", "will launch", "to be released"]
    
    def __init__(self, ticker: str, headless: bool = True):
        super().__init__(headless)
        self.ticker = ticker
        
        from app.core.constants import TICKER_NAME_MAP
        search_name = TICKER_NAME_MAP.get(ticker, ticker)
        
        # 개선된 검색 쿼리: 미래 지향적 키워드 사용
        # "예정", "계획"을 포함하여 미래 이벤트만 검색
        self.search_query = f"{search_name} (예정 OR 계획 OR 출시예정 OR upcoming OR scheduled OR 상반기 OR 하반기)"
        encoded_query = quote(self.search_query)
        
        # Google News RSS URL (Korean, Korea region)
        self.rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        
        # Also search in English for international tickers
        self.search_query_en = f"{ticker} (upcoming OR scheduled OR expected OR planned OR launch date)"
        encoded_query_en = quote(self.search_query_en)
        self.rss_url_en = f"https://news.google.com/rss/search?q={encoded_query_en}&hl=en&gl=US&ceid=US:en"

    def _contains_future_keyword(self, text: str) -> bool:
        """Check if text contains future-oriented keywords."""
        text_lower = text.lower()
        for kw in self.FUTURE_KEYWORDS_KR + self.FUTURE_KEYWORDS_EN:
            if kw.lower() in text_lower:
                return True
        return False

    def _is_past_tense(self, text: str) -> bool:
        """Check if text indicates past event (already happened)."""
        past_indicators_kr = ["출시했", "발표했", "공개했", "선보였", "개최했", "열렸", "발매됐", "나왔"]
        past_indicators_en = ["launched", "released", "announced", "unveiled", "revealed", "debuted"]
        
        text_lower = text.lower()
        for indicator in past_indicators_kr + past_indicators_en:
            if indicator in text_lower:
                return True
        return False

    async def run(self) -> List[Dict[str, Any]]:
        """
        Fetch news via RSS and return items for GPT processing.
        Does NOT assign default dates - GPT will extract dates.
        """
        print(f"Fetching RSS for {self.ticker}...")
        discovered_events = []
        
        # Fetch both Korean and English news
        urls_to_fetch = [
            (self.rss_url, "KR"),
            (self.rss_url_en, "EN")
        ]
        
        async with httpx.AsyncClient() as client:
            for rss_url, lang in urls_to_fetch:
                try:
                    response = await client.get(rss_url, timeout=10.0)
                    
                    if response.status_code != 200:
                        print(f"  Failed to fetch {lang} RSS: {response.status_code}")
                        continue
                    
                    # Parse XML
                    root = ET.fromstring(response.content)
                    items = root.findall(".//item")
                    
                    print(f"  Found {len(items)} {lang} news items")
                    
                    # Process top 10 items per language
                    for item in items[:10]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        description = item.find("description").text if item.find("description") is not None else ""
                        
                        if not title:
                            continue
                        
                        # Clean title (remove source at the end, e.g. " - 뉴스1")
                        if " - " in title:
                            title = title.rsplit(" - ", 1)[0]
                        
                        # Pre-filter: Skip obvious past events
                        if self._is_past_tense(title):
                            print(f"    Skip (past): {title[:40]}...")
                            continue
                        
                        # Preference for items with future keywords
                        has_future_keyword = self._contains_future_keyword(title) or self._contains_future_keyword(description)
                        
                        # NO default date - GPT will extract or return null
                        discovered_events.append({
                            "type": "DISCOVERY",
                            "ticker": self.ticker,
                            "title": title,
                            "description": description[:500] if description else "",  # Limit length
                            "source_url": link,
                            "crawled_at": datetime.now().isoformat(),
                            "pub_date": pub_date,
                            "target_date": None,  # GPT will extract
                            "has_future_keyword": has_future_keyword,
                            "language": lang
                        })
                        
                except Exception as e:
                    print(f"  Error fetching {lang} RSS: {e}")
        
        # Sort: prioritize items with future keywords
        discovered_events.sort(key=lambda x: (not x.get("has_future_keyword", False)))
        
        print(f"  Total: {len(discovered_events)} news items for GPT processing")
        return discovered_events
