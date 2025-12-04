from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.scheduler import scheduler_service

router = APIRouter()

@router.post("/crawl/manual")
async def trigger_manual_crawl(background_tasks: BackgroundTasks):
    """
    Manually trigger the daily update job.
    This runs in the background to avoid blocking the request.
    """
    try:
        # Run in background to return response immediately
        background_tasks.add_task(scheduler_service.trigger_manual_update)
        return {"message": "Manual crawl triggered successfully. Check logs for progress."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger crawl: {str(e)}")

@router.get("/crawl/debug")
async def debug_crawl():
    """
    Debug endpoint to test crawler synchronously.
    """
    try:
        from app.core.constants import TARGET_TICKERS, TICKER_NAME_MAP
        from app.services.crawler.discovery import EventDiscoveryCrawler
        
        results = {}
        
        # Check Tickers
        results["target_tickers_count"] = len(TARGET_TICKERS)
        results["ticker_map_count"] = len(TICKER_NAME_MAP)
        results["sample_ticker_map"] = {k: TICKER_NAME_MAP[k] for k in list(TICKER_NAME_MAP.keys())[:5]}
        
        # Test MSFT
        crawler = EventDiscoveryCrawler("MSFT")
        msft_events = await crawler.run()
        results["msft_events"] = msft_events
        
        return results
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
