from typing import List, Dict, Any, Optional
from app.services.crawler.base import BaseCrawler
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote

class TypeANewsCrawler(BaseCrawler):
    """
    Type A (Fact) Crawler: News Search (RSS Version)
    
    목표: '확정된 일정'을 찾기 위해 뉴스를 검색하고 결과를 수집합니다.
    예시: "출시일 확정", "공개 예정" 등의 키워드로 검색하여 날짜 정보가 있는 뉴스를 찾습니다.
    방법: Google News RSS를 통해 안정적으로 데이터 수집.
    """
    
    def __init__(self, keyword: str, headless: bool = True):
        super().__init__(headless)
        self.keyword = keyword
        # Google News RSS URL (Korean, Korea region)
        encoded_keyword = quote(keyword)
        self.rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"

    async def run(self) -> List[Dict[str, Any]]:
        """
        Fetch news via RSS and return structured results.
        """
        print(f"Fetching news for keyword: {self.keyword}...")
        results = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.rss_url, timeout=15.0)
                
                if response.status_code != 200:
                    print(f"Failed to fetch RSS for {self.keyword}: {response.status_code}")
                    return []
                
                # Parse XML
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in items[:20]:  # Limit to top 20 items
                    title = item.find("title").text if item.find("title") is not None else "No Title"
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    description = item.find("description").text if item.find("description") is not None else ""
                    
                    # Clean title (remove source at the end, e.g. " - 뉴스1")
                    source = ""
                    if " - " in title:
                        parts = title.rsplit(" - ", 1)
                        title = parts[0]
                        source = parts[1] if len(parts) > 1 else ""
                    
                    results.append({
                        "type": "TYPE_A",
                        "source": source or "Google News",
                        "keyword": self.keyword,
                        "title": title,
                        "link": link,
                        "summary": description,
                        "pub_date": pub_date,
                        "crawled_at": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"Error fetching RSS for {self.keyword}: {e}")
            
        return results
