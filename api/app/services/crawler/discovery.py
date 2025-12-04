from typing import List, Dict, Any, Optional
from playwright.async_api import Browser
from app.services.crawler.base import BaseCrawler
from datetime import datetime, timedelta
import re

class EventDiscoveryCrawler(BaseCrawler):
    """
    Event Discovery Crawler
    
    목표: 특정 종목(키워드)과 관련된 미래 이벤트(일정)를 발견합니다.
    방법: 네이버/구글 검색을 통해 '일정', '출시', '발표', '공개' 등의 키워드와 조합하여 검색.
    """
    
    def __init__(self, ticker: str, headless: bool = True):
        super().__init__(headless)
        self.ticker = ticker
        # 검색 쿼리 조합: "{종목명} 일정", "{종목명} 출시", "{종목명} 발표"
        # 여기서는 단순화를 위해 하나만 예시로 사용하거나, 여러 페이지를 방문할 수 있음.
        self.search_query = f"{ticker} 주요 일정 발표 출시"
        self.base_url = f"https://search.naver.com/search.naver?where=news&query={self.search_query}&sm=tab_opt&sort=1" # sort=1 (최신순)

    async def crawl(self, browser: Browser) -> List[Dict[str, Any]]:
        # Create context with User-Agent to avoid bot detection and get consistent desktop view
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 1. 네이버 뉴스 검색 (최신순)
        await page.goto(self.base_url)
        try:
            # Wait for the body or the list container
            await page.wait_for_selector("body", timeout=5000)
        except:
            print(f"Timeout waiting for body for {self.ticker}")
            await context.close()
            return []
        
        # Try to find items using the class we saw in debugging: api_subject_bx
        # This seems to be the container for news items in the new Fender UI
        news_items = await page.query_selector_all("div.api_subject_bx")
        
        # Fallback to .news_wrap if api_subject_bx is not found (legacy view)
        if not news_items:
             news_items = await page.query_selector_all(".news_wrap")
        
        # Fallback to .bx if neither found
        if not news_items:
             news_items = await page.query_selector_all("li.bx")

        discovered_events = []
        
        for item in news_items:
            # Try to find the title link. 
            # In Fender UI, it's usually the first 'a' tag with some text, or we can look for specific classes if we knew them.
            # But since classes are dynamic, let's look for the 'a' tag that is likely the title.
            # Usually it's an 'a' tag that contains the title text.
            # Let's try to find an 'a' tag that has a non-empty text and href.
            
            # Strategy: Get all links, pick the one with the longest text (heuristic) or the first one.
            links = await item.query_selector_all("a")
            title_el = None
            for link in links:
                text = await link.inner_text()
                if len(text) > 10: # Assuming titles are reasonably long
                    title_el = link
                    break
            
            if not title_el:
                continue

            title = await title_el.inner_text()
            link = await title_el.get_attribute("href")
            
            # 요약문 (Description)
            # Try to find a div or p that looks like a description
            desc = ""
            # This is hard without stable classes. We'll skip description for now or try a generic approach.
            
            # 날짜 추출 시도 (매우 단순한 정규식 사용)
            # 예: "12월 5일", "2024년 1월", "다음달" 등
            # 실제로는 NLP나 더 복잡한 파싱이 필요함.
            # 여기서는 제목이나 내용에 '일', '월'이 포함되어 있고 미래 시점 같으면 후보로 등록.
            
            # 간단한 필터: '공개', '출시', '발표', '개최', '예정' 등의 단어가 있는지
            keywords = ['공개', '출시', '발표', '개최', '예정', '일정', '컨퍼런스', '실적']
            if any(k in title for k in keywords):
                 discovered_events.append({
                    "type": "DISCOVERY",
                    "ticker": self.ticker,
                    "title": title,
                    "description": desc,
                    "source_url": link,
                    "crawled_at": datetime.now().isoformat()
                })

        await context.close()
        return discovered_events

    def parse(self, html_content: str) -> Optional[Dict[str, Any]]:
        pass
