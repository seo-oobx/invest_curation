from supabase import create_client, Client
from app.core.config import get_settings

settings = get_settings()

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_db():
    # In Supabase-py, the client is stateless and can be reused.
    # If we were using SQLAlchemy, we would yield a session here.
    # For now, we return the client directly.
    return supabase
