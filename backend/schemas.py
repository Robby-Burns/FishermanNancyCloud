from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CatchCreate(BaseModel):
    """Create a new catch log"""
    fish_type: str = Field(..., description="Type of fish: Crab, Salmon, Halibut, Other")
    pounds: float = Field(..., gt=0, description="Pounds caught")
    date: Optional[datetime] = None


class CatchResponse(BaseModel):
    """Catch log response"""
    id: int
    date: datetime
    fish_type: str
    pounds: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class BuyerCreate(BaseModel):
    """Create a new buyer"""
    name: str
    phone: str = Field(..., pattern=r"^\d{10}$", description="10-digit phone number")
    carrier: str = Field(..., pattern=r"^(verizon|att|tmobile|sprint)$")
    email: Optional[str] = None
    preferred_fish: Optional[str] = None
    notes: Optional[str] = None


class BuyerResponse(BaseModel):
    """Buyer response"""
    id: int
    name: str
    phone: str
    carrier: str
    email: Optional[str]
    preferred_fish: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PriceResponse(BaseModel):
    """Price response"""
    id: int
    fish_type: str
    price_per_lb: float
    cannery_name: str
    scraped_at: datetime
    
    class Config:
        from_attributes = True


class MessageDraft(BaseModel):
    """Generated message draft"""
    message_id: Optional[int] = None
    buyer_id: int
    buyer_name: str
    message_text: str
    catch_id: int
    fish_type: str
    pounds: float
    price_per_lb: float


class MessageSend(BaseModel):
    """Send an approved message"""
    message_id: int


class MessageResponse(BaseModel):
    """Message response"""
    id: int
    buyer_id: int
    catch_id: Optional[int]
    message_text: str
    sent_at: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True


class ContactBuyersRequest(BaseModel):
    """Request to contact buyers about a catch"""
    catch_id: int


class ContactBuyersResponse(BaseModel):
    """Response with message drafts"""
    drafts: List[MessageDraft]
    violations: List[dict]
    price_data: dict


class SaleCreate(BaseModel):
    """Log a completed sale"""
    catch_id: int
    buyer_id: int
    pounds_sold: float = Field(..., gt=0)
    final_price: float = Field(..., gt=0)
    meetup_details: Optional[str] = None


class SaleResponse(BaseModel):
    """Sale response"""
    id: int
    catch_id: int
    buyer_id: int
    pounds_sold: float
    final_price: float
    meetup_details: Optional[str]
    completed_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request"""
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str = "bearer"


class CanneryCreate(BaseModel):
    """Add a cannery"""
    name: str
    url: str


class CanneryResponse(BaseModel):
    """Cannery response"""
    id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    agent: str


class CoachingEventResponse(BaseModel):
    """Coaching event response"""
    event_id: str
    timestamp: datetime
    guardrail: str
    severity: str
    violation_description: str
    coaching_delivered: str
    
    class Config:
        from_attributes = True
