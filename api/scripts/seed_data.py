import asyncio
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

# Add api directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import supabase

load_dotenv()

async def seed_data():
    print("Seeding data...")
    
    # 1. Clear existing data (Optional, be careful in production)
    # supabase.table("events").delete().neq("id", 0).execute()

    # 2. Create Dummy Events
    events = [
        {
            "title": "GTA 6 Trailer 2 Release",
            "target_date": (date.today() + timedelta(days=45)).isoformat(),
            "is_date_confirmed": False,
            "event_type": "TYPE_A",
            "hype_score": 85,
            "related_tickers": ["TTWO", "SONY"],
            "status": "ACTIVE"
        },
        {
            "title": "Samsung Galaxy Z Fold 7 Unpacked",
            "target_date": (date.today() + timedelta(days=120)).isoformat(),
            "is_date_confirmed": True,
            "event_type": "TYPE_A",
            "hype_score": 72,
            "related_tickers": ["005930", "009150"],
            "status": "ACTIVE"
        },
        {
            "title": "Tesla Robotaxi Day 2.0",
            "target_date": (date.today() + timedelta(days=15)).isoformat(),
            "is_date_confirmed": False,
            "event_type": "TYPE_B",
            "hype_score": 94,
            "related_tickers": ["TSLA"],
            "status": "ACTIVE"
        }
    ]

    for event in events:
        print(f"Inserting event: {event['title']}")
        res = supabase.table("events").insert(event).execute()
        
        if res.data:
            event_id = res.data[0]['id']
            
            # 3. Create Dummy Hype Metrics (History)
            metrics = []
            for i in range(7):
                day = date.today() - timedelta(days=6-i)
                base_score = event['hype_score'] - (6-i)*2 # Increasing trend
                metrics.append({
                    "event_id": event_id,
                    "recorded_at": day.isoformat(),
                    "search_volume": base_score * 10 + (i*50),
                    "community_buzz": base_score + (i*2),
                    "youtube_count": int(base_score / 5) + i
                })
            
            supabase.table("hype_metrics").insert(metrics).execute()
            print(f"  -> Added metrics for event {event_id}")

    print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())
