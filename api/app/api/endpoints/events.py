from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.db.session import get_db
from supabase import Client

router = APIRouter()

@router.get("/", response_model=List[EventResponse])
def read_events(
    skip: int = 0, 
    limit: int = 100, 
    db: Client = Depends(get_db)
):
    """
    Retrieve active events.
    """
    # Supabase-py query
    response = db.table("events").select("*").range(skip, skip + limit - 1).execute()
    return response.data

@router.get("/{event_id}", response_model=EventResponse)
def read_event(event_id: int, db: Client = Depends(get_db)):
    """
    Get a specific event by ID.
    """
    response = db.table("events").select("*, hype_metrics(*), event_proxies(*)").eq("id", event_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Map relationships manually if needed, but Supabase returns nested JSON 
    # which matches our Pydantic model structure (hype_metrics, proxies)
    # Note: Supabase returns 'event_proxies' but our model expects 'proxies'.
    # We might need a validator or alias in Pydantic, or map it here.
    # Let's adjust the Pydantic model alias in a future step if needed.
    # For now, let's assume the DB relationship name matches or we map it.
    
    event_data = response.data[0]
    # Simple mapping for 'event_proxies' -> 'proxies' if needed
    if 'event_proxies' in event_data:
        event_data['proxies'] = event_data.pop('event_proxies')
        
    return event_data

@router.post("/", response_model=EventResponse)
def create_event(event: EventCreate, db: Client = Depends(get_db)):
    """
    Create a new event.
    """
    # Convert Pydantic model to dict, exclude unset
    event_data = event.model_dump(exclude_unset=True)
    
    # Convert date/enum objects to strings if needed (Supabase-py handles most)
    event_data['target_date'] = event_data['target_date'].isoformat()
    event_data['event_type'] = event.event_type.value
    event_data['status'] = event.status.value
    
    response = db.table("events").insert(event_data).execute()
    
    if not response.data:
         raise HTTPException(status_code=400, detail="Could not create event")
         
    return response.data[0]
