from typing import List, Dict, Any, Optional
from playwright.async_api import Browser
from app.services.crawler.base import BaseCrawler
from datetime import datetime, timedelta

class TypeBHypeCrawler(BaseCrawler):
    """
    Type B (Hype) Crawler: Community Buzz Check
    
    목표: 사람들이 이 주제에 대해 얼마나 떠들고 있는지(Hype)를 측정합니다.
    방법: 네이버 '뷰(View)' 탭(블로그+카페)에서 키워드를 검색하고, 
          최근 1주일 내에 작성된 게시글이 몇 개나 상단에 노출되는지 셉니다.
    """
    
    def __init__(self, keyword: str, headless: bool = True):
        super().__init__(headless)
        self.keyword = keyword
        # 네이버 뷰(View) 검색 URL
        self.base_url = f"https://search.naver.com/search.naver?where=view&query={keyword}"

    async def crawl(self, browser: Browser) -> List[Dict[str, Any]]:
        # 1. 인턴에게 "네이버 블로그/카페 검색 탭으로 가"라고 지시
        page = await browser.new_page()
        await page.goto(self.base_url)
        
        # 2. 검색 결과가 뜰 때까지 대기
        await page.wait_for_selector(".view_wrap")
        
        # 3. 화면에 보이는 게시글 덩어리들을 다 가져옴
        posts = await page.query_selector_all(".view_wrap")
        
        recent_post_count = 0
        crawled_data = []
        
        # 오늘 날짜 기준 7일 전
        one_week_ago = datetime.now() - timedelta(days=7)
        
        for post in posts:
            # 날짜 정보 가져오기 (예: "1시간 전", "2023.11.30.")
            date_el = await post.query_selector(".sub_time")
            if not date_el:
                continue
                
            date_text = await date_el.inner_text()
            
            # 간단한 로직: "전" (1시간 전, 3일 전) 이라는 글자가 있거나,
            # 날짜가 최근 1주일 이내인지 확인 (여기서는 단순화해서 '전'이 포함되면 최근으로 간주)
            # 실제로는 더 정교한 날짜 파싱이 필요합니다.
            is_recent = "전" in date_text 
            
            if is_recent:
                recent_post_count += 1
                title_el = await post.query_selector(".title_link")
                title = await title_el.inner_text() if title_el else "No Title"
                
                crawled_data.append({
                    "title": title,
                    "date_text": date_text
                })

        await page.close()
        
        # 결과 리턴: "최근 1주일간 핫한 게시글 개수"를 Hype 점수로 사용
        return [{
            "type": "TYPE_B",
            "source": "Naver View",
            "keyword": self.keyword,
            "hype_score_proxy": recent_post_count, # 이 숫자가 높으면 Hype이 높은 것!
            "recent_posts": crawled_data,
            "crawled_at": datetime.now().isoformat()
        }]

    def parse(self, html_content: str) -> Optional[Dict[str, Any]]:
        pass
