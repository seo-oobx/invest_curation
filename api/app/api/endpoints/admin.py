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
