from typing import List, Dict, Any, Optional
from playwright.async_api import Browser, Page
from app.services.crawler.base import BaseCrawler
from datetime import datetime

class TypeANewsCrawler(BaseCrawler):
    """
    Type A (Fact) Crawler: News Search
    
    목표: '확정된 일정'을 찾기 위해 뉴스 사이트에서 특정 키워드로 검색하고 결과를 수집합니다.
    예시: "출시일 확정", "공개 예정" 등의 키워드로 검색하여 날짜 정보가 있는 뉴스를 찾습니다.
    """
    
    def __init__(self, keyword: str, headless: bool = True):
        super().__init__(headless)
        self.keyword = keyword
        # 네이버 뉴스 검색 URL (query parameter로 검색어 전달)
        self.base_url = f"https://search.naver.com/search.naver?where=news&query={keyword}"

    async def crawl(self, browser: Browser) -> List[Dict[str, Any]]:
        # 1. 브라우저에서 새 탭(Page)을 엽니다. (마치 크롬 탭 하나 띄우는 것과 같음)
        page = await browser.new_page()
        
        # 2. 검색 결과 페이지로 이동합니다.
        await page.goto(self.base_url)
        
        # 3. 뉴스 리스트가 로딩될 때까지 기다립니다. (사람이 눈으로 확인하는 시간 확보)
        # 'news_area'라는 클래스를 가진 요소가 나타날 때까지 대기
        await page.wait_for_selector(".news_area")
        
        # 4. 뉴스 아이템들을 모두 가져옵니다.
        news_elements = await page.query_selector_all(".news_area")
        
        results = []
        for element in news_elements:
            # 각 뉴스 박스에서 제목과 링크, 요약문을 추출합니다.
            title_el = await element.query_selector(".news_tit")
            summary_el = await element.query_selector(".news_dsc")
            
            if title_el:
                title = await title_el.inner_text()
                link = await title_el.get_attribute("href")
                summary = await summary_el.inner_text() if summary_el else ""
                
                results.append({
                    "type": "TYPE_A",
                    "source": "Naver News",
                    "keyword": self.keyword,
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "crawled_at": datetime.now().isoformat()
                })
                
        await page.close()
        return results

    def parse(self, html_content: str) -> Optional[Dict[str, Any]]:
        # 이 예제에서는 crawl 메서드 안에서 직접 파싱하므로 여기서는 사용하지 않습니다.
        # 복잡한 페이지의 경우 HTML만 가져와서 여기서 BeautifulSoup으로 파싱하기도 합니다.
        pass
