from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field

class EventDetails(BaseModel):
    """Model to store event details extracted from websites."""
    title: str
    description: Optional[str] = None
    venue: str
    location: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prices: List[Dict[str, str]] = Field(default_factory=list)
    image_url: Optional[HttpUrl] = None
    event_url: HttpUrl
    source: str  # 'webtickets' or 'computicket'
    raw_data: Dict[str, Any] = Field(default_factory=dict)  # Store raw data for debugging
