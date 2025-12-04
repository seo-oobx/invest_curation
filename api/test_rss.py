import asyncio
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote

async def test_rss():
    ticker = "삼성전자"
    # Keywords: 일정, 발표, 출시, 공개
    query = f"{ticker} 일정 OR 발표 OR 출시 OR 공개"
    encoded_query = quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    print(f"Fetching RSS: {url}")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # RSS 2.0 structure: channel -> item
            items = root.findall(".//item")
            print(f"Found {len(items)} items.")
            
            for item in items[:5]:
                title = item.find("title").text
                link = item.find("link").text
                pubDate = item.find("pubDate").text
                print(f"- {title}")
                print(f"  Link: {link}")
                print(f"  Date: {pubDate}")

if __name__ == "__main__":
    asyncio.run(test_rss())
