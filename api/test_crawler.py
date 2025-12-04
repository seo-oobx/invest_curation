import asyncio
from app.services.crawler.discovery import EventDiscoveryCrawler

async def test_crawler():
    print("Testing EventDiscoveryCrawler for '삼성전자'...")
    crawler = EventDiscoveryCrawler(ticker="삼성전자", headless=True)
    try:
        # We need to access the internal crawl method or modify the class to debug.
        # Since I can't easily modify the class just for testing without changing the file, 
        # I will modify the test script to instantiate the browser manually and run the logic 
        # similar to the crawler to debug.
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Create context with User-Agent
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            url = f"https://search.naver.com/search.naver?where=news&query=삼성전자 주요 일정 발표 출시&sm=tab_opt&sort=1"
            print(f"Navigating to {url}")
            await page.goto(url)
            await page.wait_for_selector("body", timeout=5000)
            
            body_text = await page.inner_text("body")
            print(f"Body text snippet: {body_text[:500]}")
            
            # Try to find items using the class we saw in debugging: api_subject_bx
            news_items = await page.query_selector_all("div.api_subject_bx")
            
            # Fallback to .news_wrap if api_subject_bx is not found (legacy view)
            if not news_items:
                 news_items = await page.query_selector_all(".news_wrap")
            
            # Fallback to .bx if neither found
            if not news_items:
                 news_items = await page.query_selector_all("li.bx")

            print(f"Found {len(news_items)} items.")
            
            for item in news_items:
                links = await item.query_selector_all("a")
                title_el = None
                for link in links:
                    text = await link.inner_text()
                    if len(text) > 10: 
                        title_el = link
                        break
                
                if title_el:
                    print(f"Title: {await title_el.inner_text()}")
                    print(f"Link: {await title_el.get_attribute('href')}")
            
            await browser.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_crawler())
