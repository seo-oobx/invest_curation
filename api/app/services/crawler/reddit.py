"""
Reddit Crawler

Fetches posts from Reddit subreddits using the public JSON API.
No authentication required for public subreddits.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import httpx
from urllib.parse import quote


class RedditCrawler:
    """
    Reddit Crawler using public JSON API.
    
    Subreddits: r/stocks, r/investing, r/wallstreetbets
    """
    
    # Subreddits to crawl for stock-related content
    SUBREDDITS = ["stocks", "investing", "wallstreetbets"]
    
    def __init__(self, keyword: str):
        """
        Initialize Reddit crawler with a search keyword.
        
        Args:
            keyword: Stock ticker or company name to search for
        """
        self.keyword = keyword
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    async def run(self) -> Dict[str, Any]:
        """
        Search Reddit for posts mentioning the keyword.
        
        Returns:
            Dict with post_count, total_score, total_comments, and posts list
        """
        all_posts = []
        total_score = 0
        total_comments = 0
        
        async with httpx.AsyncClient() as client:
            for subreddit in self.SUBREDDITS:
                try:
                    posts = await self._search_subreddit(client, subreddit)
                    all_posts.extend(posts)
                    
                    for post in posts:
                        total_score += post.get("score", 0)
                        total_comments += post.get("num_comments", 0)
                        
                except Exception as e:
                    print(f"Error fetching from r/{subreddit}: {e}")
                    continue
        
        return {
            "source": "Reddit",
            "keyword": self.keyword,
            "post_count": len(all_posts),
            "total_score": total_score,
            "total_comments": total_comments,
            "engagement": total_score + total_comments,  # Combined engagement metric
            "posts": all_posts[:20],  # Limit to top 20 posts
            "crawled_at": datetime.now().isoformat()
        }
    
    async def _search_subreddit(
        self, 
        client: httpx.AsyncClient, 
        subreddit: str
    ) -> List[Dict[str, Any]]:
        """
        Search a specific subreddit for keyword mentions.
        """
        encoded_keyword = quote(self.keyword)
        
        # Reddit search API (public JSON endpoint)
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": encoded_keyword,
            "restrict_sr": "on",  # Restrict to this subreddit
            "sort": "relevance",
            "t": "week",  # Time filter: posts from past week
            "limit": 25
        }
        
        response = await client.get(
            url,
            params=params,
            headers={"User-Agent": self.user_agent},
            timeout=15.0
        )
        
        if response.status_code != 200:
            print(f"Reddit API returned {response.status_code} for r/{subreddit}")
            return []
        
        data = response.json()
        posts = []
        
        # Parse Reddit's response structure
        children = data.get("data", {}).get("children", [])
        
        one_week_ago = datetime.now() - timedelta(days=7)
        
        for child in children:
            post_data = child.get("data", {})
            
            # Filter for recent posts
            created_utc = post_data.get("created_utc", 0)
            post_date = datetime.fromtimestamp(created_utc)
            
            if post_date < one_week_ago:
                continue
            
            posts.append({
                "subreddit": subreddit,
                "title": post_data.get("title", ""),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                "created_at": post_date.isoformat(),
                "upvote_ratio": post_data.get("upvote_ratio", 0)
            })
        
        return posts
    
    async def get_subreddit_hot(self, subreddit: str = "stocks", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get hot posts from a subreddit (for general monitoring).
        
        Args:
            subreddit: Subreddit name
            limit: Number of posts to fetch
            
        Returns:
            List of hot posts
        """
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params={"limit": limit},
                headers={"User-Agent": self.user_agent},
                timeout=15.0
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            posts = []
            
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                posts.append({
                    "title": post_data.get("title", ""),
                    "score": post_data.get("score", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}"
                })
            
            return posts


class NaverDiscussionCrawler:
    """
    Naver Stock Discussion Board Crawler (via RSS/Search)
    
    Since Naver doesn't have a public API, we use news RSS as a proxy for Korean market buzz.
    """
    
    def __init__(self, keyword: str):
        self.keyword = keyword
        # Naver News RSS for Korean stocks
        self.rss_url = f"https://news.google.com/rss/search?q={quote(keyword)}+주식&hl=ko&gl=KR&ceid=KR:ko"
    
    async def run(self) -> Dict[str, Any]:
        """
        Fetch Korean news/discussion data for the keyword.
        """
        import xml.etree.ElementTree as ET
        
        post_count = 0
        posts = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.rss_url, timeout=15.0)
                
                if response.status_code != 200:
                    return self._empty_result()
                
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                one_week_ago = datetime.now() - timedelta(days=7)
                
                for item in items[:30]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                    
                    # Clean title
                    if " - " in title:
                        title = title.rsplit(" - ", 1)[0]
                    
                    posts.append({
                        "title": title,
                        "url": link,
                        "pub_date": pub_date
                    })
                    post_count += 1
                    
        except Exception as e:
            print(f"Error fetching Naver data for {self.keyword}: {e}")
            return self._empty_result()
        
        return {
            "source": "Naver/Korean News",
            "keyword": self.keyword,
            "post_count": post_count,
            "posts": posts[:20],
            "crawled_at": datetime.now().isoformat()
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        return {
            "source": "Naver/Korean News",
            "keyword": self.keyword,
            "post_count": 0,
            "posts": [],
            "crawled_at": datetime.now().isoformat()
        }

