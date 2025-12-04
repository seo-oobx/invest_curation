from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote

class TypeBHypeCrawler:
    """
    Type B (Hype) Crawler: Community Buzz Check (RSS Version)
    
    목표: 사람들이 이 주제에 대해 얼마나 떠들고 있는지(Hype)를 측정합니다.
    방법: Google News RSS를 통해 키워드 관련 뉴스를 검색하고,
          최근 1주일 내에 작성된 기사가 몇 개나 있는지 셉니다.
    장점: 브라우저 없이 빠르고 안정적으로 데이터 수집 가능.
    """
    
    def __init__(self, keyword: str, headless: bool = True):
        self.keyword = keyword
        # Google News RSS URL (Korean, Korea region)
        encoded_keyword = quote(keyword)
        self.rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"

    def parse_pub_date(self, pub_date_str: str) -> Optional[datetime]:
        """
        Parse RSS pubDate format (e.g., "Mon, 02 Dec 2024 10:30:00 GMT")
        Returns datetime object or None if parsing fails.
        """
        try:
            # RFC 2822 format commonly used in RSS
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(pub_date_str)
        except:
            return None

    async def run(self) -> List[Dict[str, Any]]:
        """
        Fetch news via RSS and count recent articles as hype proxy.
        """
        print(f"Fetching hype data for keyword: {self.keyword}...")
        
        recent_post_count = 0
        crawled_data = []
        one_week_ago = datetime.now(tz=None) - timedelta(days=7)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.rss_url, timeout=15.0)
                
                if response.status_code != 200:
                    print(f"Failed to fetch RSS for {self.keyword}: {response.status_code}")
                    return [{
                        "type": "TYPE_B",
                        "source": "Google News RSS",
                        "keyword": self.keyword,
                        "hype_score_proxy": 0,
                        "recent_posts": [],
                        "crawled_at": datetime.now().isoformat(),
                        "error": f"HTTP {response.status_code}"
                    }]
                
                # Parse XML
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in items:
                    title = item.find("title").text if item.find("title") is not None else "No Title"
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date_str = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    
                    # Clean title (remove source at the end, e.g. " - 뉴스1")
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                    
                    # Parse publication date and check if recent
                    pub_date = self.parse_pub_date(pub_date_str)
                    is_recent = False
                    
                    if pub_date:
                        # Make pub_date timezone-naive for comparison
                        pub_date_naive = pub_date.replace(tzinfo=None)
                        is_recent = pub_date_naive >= one_week_ago
                    else:
                        # If we can't parse date, assume it's recent (conservative)
                        is_recent = True
                    
                    if is_recent:
                        recent_post_count += 1
                        crawled_data.append({
                            "title": title,
                            "link": link,
                            "date_text": pub_date_str
                        })
                        
        except Exception as e:
            print(f"Error fetching RSS for {self.keyword}: {e}")
            return [{
                "type": "TYPE_B",
                "source": "Google News RSS",
                "keyword": self.keyword,
                "hype_score_proxy": 0,
                "recent_posts": [],
                "crawled_at": datetime.now().isoformat(),
                "error": str(e)
            }]
        
        # 결과 리턴: "최근 1주일간 핫한 기사/게시글 개수"를 Hype 점수로 사용
        return [{
            "type": "TYPE_B",
            "source": "Google News RSS",
            "keyword": self.keyword,
            "hype_score_proxy": recent_post_count,  # 이 숫자가 높으면 Hype이 높은 것!
            "recent_posts": crawled_data[:20],  # Limit to top 20 for response size
            "crawled_at": datetime.now().isoformat()
        }]
