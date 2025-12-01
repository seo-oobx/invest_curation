from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

# Enums
class EventType(str, Enum):
    TYPE_A = 'TYPE_A'
    TYPE_B = 'TYPE_B'

class EventStatus(str, Enum):
    ACTIVE = 'ACTIVE'
    FINISHED = 'FINISHED'

class MembershipTier(str, Enum):
    FREE = 'FREE'
    PRO = 'PRO'

# --- Hype Metrics ---
class HypeMetricBase(BaseModel):
    search_volume: int = 0
    community_buzz: int = 0
    youtube_count: int = 0
    recorded_at: date

class HypeMetricCreate(HypeMetricBase):
    event_id: int

class HypeMetricResponse(HypeMetricBase):
    id: int
    event_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Event Proxies ---
class EventProxyBase(BaseModel):
    proxy_name: str
    detected_at: datetime

class EventProxyCreate(EventProxyBase):
    parent_event_id: int

class EventProxyResponse(EventProxyBase):
    id: int
    parent_event_id: int

    class Config:
        from_attributes = True

# --- Events ---
class EventBase(BaseModel):
    title: str
    target_date: date
    is_date_confirmed: bool = False
    event_type: EventType
    related_tickers: List[str] = []
    status: EventStatus = EventStatus.ACTIVE

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    target_date: Optional[date] = None
    is_date_confirmed: Optional[bool] = None
    event_type: Optional[EventType] = None
    hype_score: Optional[int] = None
    related_tickers: Optional[List[str]] = None
    status: Optional[EventStatus] = None

class EventResponse(EventBase):
    id: int
    hype_score: int
    created_at: datetime
    updated_at: datetime
    
    # Optional relationships
    hype_metrics: List[HypeMetricResponse] = []
    proxies: List[EventProxyResponse] = []

    class Config:
        from_attributes = True
