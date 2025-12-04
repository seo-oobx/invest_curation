"""
Scheduler Service

Main daily job pipeline:
1. Discovery: Crawl news for each target ticker
2. GPT Extraction: Extract ONLY future events (2-6 months) with explicit dates
3. Multi-source Hype: Collect data from News, Reddit, Naver
4. Score Calculation: Weighted hype score
5. Auto-publish: ACTIVE if score >= 50 AND confidence >= 0.7

STRICT RULE: Events WITHOUT explicit future dates are NOT saved.
"""

import asyncio
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import get_db
from app.services.hype_calculator import HypeCalculator


class SchedulerService:
    """
    Main scheduler service for daily event discovery and hype calculation.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.supabase = get_db()
        self._is_running = False

    def start(self, run_immediately: bool = False):
        """Start the scheduler."""
        self.scheduler.add_job(self.daily_update_job, 'cron', hour=0, minute=0, id='daily_update')
        self.scheduler.start()
        print("Scheduler started...")
        
        should_run_immediately = run_immediately or os.getenv("RUN_CRAWLER_ON_STARTUP", "false").lower() == "true"
        
        if should_run_immediately:
            print("Scheduling immediate crawl on startup...")
            self.scheduler.add_job(
                self.daily_update_job, 
                'date', 
                run_date=datetime.now() + timedelta(seconds=5),
                id='startup_crawl'
            )

    def shutdown(self):
        self.scheduler.shutdown()
        print("Scheduler shut down...")

    async def daily_update_job(self):
        """Main daily pipeline."""
        if self._is_running:
            print("Job already running, skipping...")
            return
            
        self._is_running = True
        print(f"\n{'='*60}")
        print(f"[{datetime.now()}] Starting daily update job...")
        print(f"{'='*60}\n")
        
        try:
            await self._phase_discovery()
            await self._phase_hype_calculation()
            
            print(f"\n{'='*60}")
            print(f"[{datetime.now()}] Daily update job completed.")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"Critical error in daily job: {e}")
        finally:
            self._is_running = False

    async def _phase_discovery(self):
        """
        Phase 1: Discover new FUTURE events using news + GPT.
        
        STRICT: Only saves events where GPT successfully extracts a future date.
        No fallback to default dates.
        """
        from app.core.constants import TARGET_TICKERS
        from app.services.crawler.discovery import EventDiscoveryCrawler
        from app.services.openai_service import openai_service
        
        print(f"\n[Phase 1] Event Discovery for {len(TARGET_TICKERS)} tickers...")
        print("STRICT MODE: Only events with GPT-extracted future dates will be saved.\n")
        
        events_created = 0
        events_skipped_no_date = 0
        events_skipped_exists = 0
        
        for i, ticker in enumerate(TARGET_TICKERS):
            print(f"\n[{i+1}/{len(TARGET_TICKERS)}] Processing {ticker}...")
            
            try:
                # Step 1: Crawl news
                discovery_crawler = EventDiscoveryCrawler(ticker=ticker)
                news_items = await discovery_crawler.run()
                
                if not news_items:
                    print(f"  No news found for {ticker}")
                    continue
                
                print(f"  Found {len(news_items)} news items, sending to GPT...")
                
                # Step 2: Extract events using GPT (limit to top 5 news)
                for news in news_items[:5]:
                    title = news.get('title', '')
                    if not title or len(title) < 10:
                        continue
                    
                    # Check if event with similar title exists
                    try:
                        existing = self.supabase.table("events")\
                            .select("id")\
                            .ilike("title", f"%{title[:40]}%")\
                            .execute()
                        
                        if existing.data:
                            events_skipped_exists += 1
                            continue
                    except Exception:
                        pass
                    
                    # GPT extraction - the ONLY way to create events
                    gpt_event = await openai_service.extract_event_from_news(
                        ticker=ticker,
                        news_title=title,
                        news_summary=news.get('description', '')
                    )
                    
                    # STRICT: Only save if GPT found a valid future event with date
                    if not gpt_event:
                        events_skipped_no_date += 1
                        continue
                    
                    if not gpt_event.get('event_title') or not gpt_event.get('event_date'):
                        events_skipped_no_date += 1
                        continue
                    
                    # Create event from GPT data
                    event_data = self._create_event_from_gpt(
                        ticker=ticker,
                        news=news,
                        gpt_event=gpt_event
                    )
                    
                    if event_data:
                        try:
                            self.supabase.table("events").insert(event_data).execute()
                            events_created += 1
                            print(f"  ✓ Created: {event_data['title'][:40]}... @ {event_data['target_date']}")
                        except Exception as e:
                            print(f"  ✗ Error inserting: {e}")
                    
                    await asyncio.sleep(0.5)  # Rate limit for GPT API
                    
            except Exception as e:
                print(f"  Error processing {ticker}: {e}")
            
            await asyncio.sleep(0.3)
        
        print(f"\n[Phase 1 Complete]")
        print(f"  ✓ Created: {events_created}")
        print(f"  ✗ Skipped (no future date): {events_skipped_no_date}")
        print(f"  ✗ Skipped (already exists): {events_skipped_exists}")

    def _create_event_from_gpt(
        self, 
        ticker: str, 
        news: Dict, 
        gpt_event: Dict
    ) -> Optional[Dict[str, Any]]:
        """
        Create event record from GPT-extracted data.
        Returns None if essential data is missing.
        """
        event_title = gpt_event.get('event_title')
        event_date = gpt_event.get('event_date')
        confidence = gpt_event.get('confidence', 0.5)
        
        # STRICT validation
        if not event_title or not event_date:
            return None
        
        # Validate date is actually in future (2-6 months)
        try:
            target_date = date.fromisoformat(event_date)
            days_until = (target_date - date.today()).days
            if days_until < 60 or days_until > 180:
                print(f"    Date {event_date} outside 2-6 month window")
                return None
        except ValueError:
            return None
        
        # Calculate initial hype score
        initial_score = 40 if confidence >= 0.8 else 30 if confidence >= 0.7 else 20
        
        # Determine status based on confidence
        status = "ACTIVE" if confidence >= 0.7 else "PENDING"
        
        return {
            "title": event_title[:200],
            "description": news.get('description', '')[:500],
            "event_type": gpt_event.get('event_type', 'TYPE_A'),
            "status": status,
            "target_date": event_date,
            "is_date_confirmed": confidence >= 0.8,
            "related_tickers": [ticker],
            "source_url": news.get('source_url', ''),
            "hype_score": initial_score,
            "gpt_confidence": confidence
        }

    async def _phase_hype_calculation(self):
        """Phase 2: Calculate multi-source hype scores for all events."""
        from app.services.crawler.type_b_hype import TypeBHypeCrawler
        from app.services.crawler.reddit import RedditCrawler, NaverDiscussionCrawler
        
        print(f"\n[Phase 2] Hype Score Calculation...")
        
        try:
            response = self.supabase.table("events")\
                .select("*")\
                .neq("status", "FINISHED")\
                .execute()
            events = response.data
        except Exception as e:
            print(f"Error fetching events: {e}")
            return
        
        if not events:
            print("No events to process.")
            return
        
        print(f"Processing {len(events)} events...")
        
        for event in events:
            event_id = event['id']
            title = event['title']
            tickers = event.get('related_tickers', [])
            
            print(f"\n  Processing: {title[:35]}... (ID: {event_id})")
            
            try:
                metrics = await self._collect_multi_source_metrics(title, tickers)
                prev_metrics = await self._get_previous_metrics(event_id)
                new_score = HypeCalculator.calculate(metrics, prev_metrics)
                
                confidence = event.get('gpt_confidence', 0.5)
                current_status = event.get('status', 'PENDING')
                
                new_status = current_status
                if current_status == "PENDING":
                    if HypeCalculator.should_auto_publish(new_score, confidence):
                        new_status = "ACTIVE"
                        print(f"    -> Auto-publishing (score: {new_score})")
                
                await self._save_metrics(event_id, metrics)
                
                self.supabase.table("events").update({
                    "hype_score": new_score,
                    "status": new_status,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", event_id).execute()
                
                print(f"    Score: {new_score} | Status: {new_status}")
                
            except Exception as e:
                print(f"    Error: {e}")
            
            await asyncio.sleep(0.3)
        
        print(f"\n[Phase 2 Complete]")

    async def _collect_multi_source_metrics(
        self, 
        keyword: str, 
        tickers: List[str]
    ) -> Dict[str, int]:
        """Collect hype metrics from multiple sources."""
        from app.services.crawler.type_b_hype import TypeBHypeCrawler
        from app.services.crawler.reddit import RedditCrawler, NaverDiscussionCrawler
        
        metrics = {
            "news_count": 0,
            "news_ranking": 0,
            "reddit_posts": 0,
            "reddit_engagement": 0,
            "naver_buzz": 0
        }
        
        try:
            news_crawler = TypeBHypeCrawler(keyword=keyword)
            news_result = await news_crawler.run()
            if news_result:
                metrics["news_count"] = news_result[0].get("hype_score_proxy", 0)
        except Exception as e:
            print(f"      News error: {e}")
        
        search_term = tickers[0] if tickers else keyword
        try:
            reddit_crawler = RedditCrawler(keyword=search_term)
            reddit_result = await reddit_crawler.run()
            metrics["reddit_posts"] = reddit_result.get("post_count", 0)
            metrics["reddit_engagement"] = reddit_result.get("engagement", 0)
        except Exception as e:
            print(f"      Reddit error: {e}")
        
        try:
            naver_crawler = NaverDiscussionCrawler(keyword=keyword)
            naver_result = await naver_crawler.run()
            metrics["naver_buzz"] = naver_result.get("post_count", 0)
        except Exception as e:
            print(f"      Naver error: {e}")
        
        return metrics

    async def _get_previous_metrics(self, event_id: int) -> Optional[Dict[str, int]]:
        """Get previous day's metrics for trend calculation."""
        try:
            result = self.supabase.table("hype_metrics")\
                .select("*")\
                .eq("event_id", event_id)\
                .order("recorded_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                prev = result.data[0]
                return {
                    "news_count": prev.get("search_volume", 0),
                    "naver_buzz": prev.get("community_buzz", 0),
                    "reddit_posts": prev.get("youtube_count", 0),
                    "reddit_engagement": 0,
                    "news_ranking": 0
                }
        except Exception as e:
            print(f"      Previous metrics error: {e}")
        
        return None

    async def _save_metrics(self, event_id: int, metrics: Dict[str, int]):
        """Save current metrics to hype_metrics table."""
        try:
            self.supabase.table("hype_metrics").insert({
                "event_id": event_id,
                "recorded_at": date.today().isoformat(),
                "search_volume": metrics.get("news_count", 0),
                "community_buzz": metrics.get("naver_buzz", 0),
                "youtube_count": metrics.get("reddit_posts", 0)
            }).execute()
        except Exception as e:
            print(f"      Save metrics error: {e}")

    async def trigger_manual_update(self):
        """Manually trigger the update job."""
        await self.daily_update_job()


scheduler_service = SchedulerService()
