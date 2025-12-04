import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import get_db
from app.services.hype_calculator import HypeCalculator

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.supabase = get_db()

    def start(self):
        # Schedule the job to run every day at 00:00 (Midnight)
        # For testing purposes, we can also trigger it manually.
        self.scheduler.add_job(self.daily_update_job, 'cron', hour=0, minute=0)
        self.scheduler.start()
        print("Scheduler started...")

    def shutdown(self):
        self.scheduler.shutdown()
        print("Scheduler shut down...")

    async def daily_update_job(self):
        print(f"[{datetime.now()}] Starting daily update job...")
        
        # 0. Discovery Phase: Find new events for target tickers
        from app.core.constants import TARGET_TICKERS
        from app.services.crawler.discovery import EventDiscoveryCrawler
        
        print(f"Starting Discovery Phase for {len(TARGET_TICKERS)} tickers...")
        for ticker in TARGET_TICKERS:
            # Simple rate limiting or batching could be added here
            print(f"Discovering events for {ticker}...")
            discovery_crawler = EventDiscoveryCrawler(ticker=ticker)
            try:
                discovered = await discovery_crawler.run()
                for event_data in discovered:
                    # Check if event already exists (simple check by title)
                    existing = self.supabase.table("events").select("id").eq("title", event_data['title']).execute()
                    if not existing.data:
                        print(f"  -> New event found: {event_data['title']}")
                        # Insert new event as INACTIVE by default
                        target_date = event_data.get('target_date')
                        if not target_date:
                             target_date = (date.today() + timedelta(days=90)).isoformat()
                        
                        self.supabase.table("events").insert({
                            "title": event_data['title'],
                            "description": event_data['description'],
                            "event_type": "TYPE_A", # Default to Type A for now
                            "status": "ACTIVE", # Auto-activate to show on main page immediately
                            "target_date": target_date,
                            "related_tickers": [ticker],
                            "source_url": event_data['source_url'],
                            "hype_score": 0
                        }).execute()
                    else:
                        print(f"  -> Event already exists: {event_data['title']}")
            except Exception as e:
                print(f"Error discovering for {ticker}: {e}")

        # 1. Fetch all ACTIVE events
        try:
            response = self.supabase.table("events").select("*").eq("status", "ACTIVE").execute()
            events = response.data
        except Exception as e:
            print(f"Error fetching events: {e}")
            return

        if not events:
            print("No active events found.")
            return

        print(f"Found {len(events)} active events. Starting crawl...")

        for event in events:
            event_id = event['id']
            title = event['title']
            print(f"Processing event: {title} (ID: {event_id})")

            # 2. Run Crawler (Type B for Hype)
            # We use the event title as the keyword for now.
            from app.services.crawler.type_b_hype import TypeBHypeCrawler
            crawler = TypeBHypeCrawler(keyword=title)
            try:
                crawl_results = await crawler.run()
            except Exception as e:
                print(f"Error crawling for {title}: {e}")
                continue

            if not crawl_results:
                print(f"No results for {title}")
                continue

            # Assuming the first result is what we want (since we search by specific keyword)
            result = crawl_results[0]
            community_buzz = result.get("hype_score_proxy", 0)

            # 3. Get previous metrics for trend calculation
            # Fetch the most recent metric before today
            prev_metrics = None
            try:
                metrics_res = self.supabase.table("hype_metrics")\
                    .select("*")\
                    .eq("event_id", event_id)\
                    .order("recorded_at", desc=True)\
                    .limit(1)\
                    .execute()
                
                if metrics_res.data:
                    prev_data = metrics_res.data[0]
                    prev_metrics = {
                        "community_buzz": prev_data.get("community_buzz", 0),
                        "search_volume": prev_data.get("search_volume", 0)
                    }
            except Exception as e:
                print(f"Error fetching previous metrics for {title}: {e}")

            # 4. Calculate Hype Score
            current_metrics = {"community_buzz": community_buzz}
            new_hype_score = HypeCalculator.calculate_score(current_metrics, prev_metrics)
            
            print(f"  -> Community Buzz: {community_buzz}, New Score: {new_hype_score}")

            # 5. Update DB
            try:
                # Insert into hype_metrics
                self.supabase.table("hype_metrics").insert({
                    "event_id": event_id,
                    "recorded_at": date.today().isoformat(),
                    "community_buzz": community_buzz,
                    "search_volume": 0, # Not crawling search volume yet
                    "youtube_count": 0  # Not crawling youtube yet
                }).execute()

                # Update events table
                self.supabase.table("events").update({
                    "hype_score": new_hype_score,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", event_id).execute()
                
            except Exception as e:
                print(f"Error updating DB for {title}: {e}")

        print(f"[{datetime.now()}] Daily update job completed.")

    async def trigger_manual_update(self):
        """
        Manually trigger the update job.
        Useful for testing or admin forcing an update.
        """
        await self.daily_update_job()

scheduler_service = SchedulerService()
