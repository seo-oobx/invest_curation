from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from app.db.session import get_db
from app.services.email_service import email_service
from supabase import Client

router = APIRouter()

class AlertRequest(BaseModel):
    email: str # In a real app, we'd get this from the JWT token

@router.post("/{event_id}")
async def toggle_alert(
    event_id: int, 
    request: AlertRequest,
    authorization: str = Header(None),
    db: Client = Depends(get_db)
):
    """
    Toggle alert subscription for a specific event.
    Requires Authorization header with Bearer token (Supabase JWT).
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = authorization.split(" ")[1]
    
    # Verify user using Supabase Auth
    try:
        user = db.auth.get_user(token)
        user_id = user.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Check if already subscribed
    existing = db.table("alerts").select("*").eq("user_id", user_id).eq("event_id", event_id).execute()
    
    if existing.data:
        # Unsubscribe
        db.table("alerts").delete().eq("user_id", user_id).eq("event_id", event_id).execute()
        return {"status": "unsubscribed", "message": "Alert removed"}
    else:
        # Subscribe
        db.table("alerts").insert({"user_id": user_id, "event_id": event_id}).execute()
        
        # Send welcome email (async in production, sync for MVP)
        # We use the email provided in request for now as Supabase user object might need extra call to get email if not in session
        # But actually user.user.email should be available
        user_email = user.user.email or request.email
        email_service.send_welcome_email(user_email, user_email.split("@")[0])
        
        return {"status": "subscribed", "message": "Alert set! Check your email."}
