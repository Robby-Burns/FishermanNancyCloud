from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import io

from backend.database import get_db, init_db, Catch, Buyer, Price, Message, Sale, Cannery, CoachingEvent
from backend.schemas import (
    CatchCreate, CatchResponse, BuyerCreate, BuyerResponse, PriceResponse,
    ContactBuyersRequest, ContactBuyersResponse, MessageSend, MessageResponse,
    SaleCreate, SaleResponse, LoginRequest, LoginResponse, CanneryCreate,
    CanneryResponse, HealthResponse, CoachingEventResponse
)
from backend.auth import authenticate, create_access_token, get_current_user
from backend.agent import FishingAgent
from backend.coach import UniversalCoach, AgentType
from backend.scraper import CanneryScraper
from backend.email_sms import EmailSMSGateway
from backend.excel_parser import ExcelParser
from backend.config import settings

# Initialize FastAPI app
app = FastAPI(title="FishCatch AI Agent API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
coach = UniversalCoach()
agent = FishingAgent(coach)
scraper = CanneryScraper()
sms_gateway = EmailSMSGateway()
excel_parser = ExcelParser()


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    init_db()
    print("FishCatch AI Agent started successfully")


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "agent": "ready"
    }


# Authentication
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with app password"""
    if not authenticate(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    access_token = create_access_token(data={"sub": "fisherman"})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Catch logging
@app.post("/api/v1/catches", response_model=CatchResponse)
async def log_catch(
    catch: CatchCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Log a new catch"""
    # Validate with agent
    validation = await agent.validate_catch_log(catch.fish_type, catch.pounds)
    
    if validation["blocked"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Catch log validation failed",
                "violations": [v["coaching"] for v in validation["violations"]]
            }
        )
    
    # Create catch
    db_catch = Catch(
        fish_type=catch.fish_type,
        pounds=catch.pounds,
        date=catch.date or datetime.utcnow()
    )
    
    db.add(db_catch)
    db.commit()
    db.refresh(db_catch)
    
    return db_catch


@app.get("/api/v1/catches", response_model=List[CatchResponse])
async def get_catches(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get catch history"""
    catches = db.query(Catch).order_by(Catch.date.desc()).limit(limit).all()
    return catches


@app.get("/api/v1/catches/stats")
async def get_catch_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get catch statistics"""
    # Total pounds by fish type
    catches = db.query(Catch).all()
    
    stats_by_fish = {}
    for catch in catches:
        if catch.fish_type not in stats_by_fish:
            stats_by_fish[catch.fish_type] = {
                "total_pounds": 0,
                "count": 0
            }
        stats_by_fish[catch.fish_type]["total_pounds"] += catch.pounds
        stats_by_fish[catch.fish_type]["count"] += 1
    
    return {
        "by_fish_type": stats_by_fish,
        "total_catches": len(catches)
    }


# Buyers
@app.post("/api/v1/buyers", response_model=BuyerResponse)
async def create_buyer(
    buyer: BuyerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new buyer"""
    db_buyer = Buyer(**buyer.dict())
    db.add(db_buyer)
    db.commit()
    db.refresh(db_buyer)
    
    return db_buyer


@app.get("/api/v1/buyers", response_model=List[BuyerResponse])
async def get_buyers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all buyers"""
    buyers = db.query(Buyer).all()
    return buyers


@app.post("/api/v1/buyers/upload-excel")
async def upload_buyers_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload Excel file with buyer contacts"""
    # Read file content
    content = await file.read()
    
    # Parse Excel
    result = excel_parser.parse_buyers_excel(content)
    
    if not result["buyers"] and result["errors"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": result["errors"]}
        )
    
    # Clear existing buyers (or update - for simplicity, we'll clear and re-add)
    db.query(Buyer).delete()
    
    # Add new buyers
    for buyer_data in result["buyers"]:
        db_buyer = Buyer(**buyer_data)
        db.add(db_buyer)
    
    db.commit()
    
    return {
        "message": f"Successfully imported {len(result['buyers'])} buyers",
        "buyers_imported": len(result["buyers"]),
        "errors": result["errors"]
    }


@app.get("/api/v1/buyers/template")
async def download_buyer_template():
    """Download Excel template for buyers"""
    excel_content = excel_parser.create_template_excel()
    
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=buyer_template.xlsx"}
    )


# Prices
@app.get("/api/v1/prices", response_model=List[PriceResponse])
async def get_prices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current prices"""
    # Get most recent price for each fish type
    prices = []
    fish_types = ["Crab", "Salmon", "Halibut"]
    
    for fish_type in fish_types:
        price = db.query(Price).filter(
            Price.fish_type == fish_type
        ).order_by(Price.scraped_at.desc()).first()
        
        if price:
            prices.append(price)
    
    return prices


@app.post("/api/v1/prices/scrape")
async def scrape_prices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Scrape cannery prices"""
    # Get active canneries
    canneries = db.query(Cannery).filter(Cannery.is_active == True).all()
    
    if not canneries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active canneries configured. Add a cannery in Settings."
        )
    
    all_prices = {}
    errors = []
    
    for cannery in canneries:
        try:
            prices = await scraper.scrape_westport_cannery(cannery.url)
            
            if prices:
                # Save prices to database
                for fish_type, price_per_lb in prices.items():
                    db_price = Price(
                        fish_type=fish_type,
                        price_per_lb=price_per_lb,
                        cannery_name=cannery.name,
                        cannery_url=cannery.url
                    )
                    db.add(db_price)
                    all_prices[fish_type] = price_per_lb
                
                db.commit()
            else:
                errors.append(f"No prices found at {cannery.name}")
        
        except Exception as e:
            errors.append(f"Error scraping {cannery.name}: {str(e)}")
    
    if not all_prices:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to scrape prices. Please enter manually.",
                "errors": errors
            }
        )
    
    return {
        "message": "Prices updated successfully",
        "prices": all_prices,
        "errors": errors
    }


@app.post("/api/v1/prices/manual")
async def add_manual_price(
    fish_type: str,
    price_per_lb: float,
    cannery_name: str = "Manual Entry",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Manually add a price"""
    db_price = Price(
        fish_type=fish_type,
        price_per_lb=price_per_lb,
        cannery_name=cannery_name
    )
    
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    
    return db_price


# Contact buyers
@app.post("/api/v1/contact-buyers", response_model=ContactBuyersResponse)
async def contact_buyers(
    request: ContactBuyersRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate message drafts for buyers"""
    # Get catch
    catch = db.query(Catch).filter(Catch.id == request.catch_id).first()
    if not catch:
        raise HTTPException(status_code=404, detail="Catch not found")
    
    # Get current price for this fish type
    price = db.query(Price).filter(
        Price.fish_type == catch.fish_type
    ).order_by(Price.scraped_at.desc()).first()
    
    # If user provided a manual base price in the request, use it
    # Note: We need to update the agent to accept this override
    # For now, we rely on the database price which might have been manually set
    
    # Get buyers who prefer this fish type
    all_buyers = db.query(Buyer).all()
    matching_buyers = [
        b for b in all_buyers
        if not b.preferred_fish or catch.fish_type in b.preferred_fish
    ]
    
    # Generate drafts with agent
    result = await agent.generate_buyer_messages(catch, price, matching_buyers, db)
    
    if result["blocked"]:
        # Check if it's just a missing price
        if result.get("missing_price"):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Price data missing",
                    "missing_price": True
                }
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot generate messages due to safety violations",
                "violations": [v["coaching"] for v in result["violations"]]
            }
        )
    
    # Save drafts to database
    draft_ids = []
    for draft in result["drafts"]:
        db_message = Message(
            buyer_id=draft["buyer_id"],
            catch_id=draft["catch_id"],
            message_text=draft["message_text"],
            status="draft"
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        draft_ids.append(db_message.id)
    
    # Add draft IDs to response
    for i, draft in enumerate(result["drafts"]):
        draft["message_id"] = draft_ids[i]
    
    return {
        "drafts": result["drafts"],
        "violations": [{"coaching": v["coaching"], "severity": v["coaching_level"].value} for v in result["violations"]],
        "price_data": {
            "fish_type": catch.fish_type,
            "price_per_lb": price.price_per_lb if price else 0,
            "cannery_name": price.cannery_name if price else "Unknown"
        }
    }


# Send message
@app.post("/api/v1/messages/send")
async def send_message(
    request: MessageSend,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send an approved message via email-to-SMS"""
    # Get message
    message = db.query(Message).filter(Message.id == request.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.status != "draft":
        raise HTTPException(status_code=400, detail="Message already sent")
    
    # Get buyer
    buyer = db.query(Buyer).filter(Buyer.id == message.buyer_id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    
    # Send via email-to-SMS
    result = sms_gateway.send_sms(buyer.phone, buyer.carrier, message.message_text)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {result['error']}"
        )
    
    # Update message status
    message.status = "sent"
    message.sent_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Message sent successfully",
        "buyer_name": buyer.name,
        "sent_at": message.sent_at
    }


# Messages / Conversations
@app.get("/api/v1/messages", response_model=List[MessageResponse])
async def get_messages(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get message history"""
    messages = db.query(Message).order_by(Message.sent_at.desc()).all()
    return messages


# Sales
@app.post("/api/v1/sales", response_model=SaleResponse)
async def log_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Log a completed sale"""
    db_sale = Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    
    return db_sale


@app.get("/api/v1/sales", response_model=List[SaleResponse])
async def get_sales(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get sales history"""
    sales = db.query(Sale).order_by(Sale.completed_at.desc()).all()
    return sales


# Canneries
@app.post("/api/v1/canneries", response_model=CanneryResponse)
async def add_cannery(
    cannery: CanneryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a cannery"""
    db_cannery = Cannery(**cannery.dict())
    db.add(db_cannery)
    db.commit()
    db.refresh(db_cannery)
    
    return db_cannery


@app.get("/api/v1/canneries", response_model=List[CanneryResponse])
async def get_canneries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all canneries"""
    canneries = db.query(Cannery).all()
    return canneries


# Coaching events (for debugging/monitoring)
@app.get("/api/v1/coaching-events", response_model=List[CoachingEventResponse])
async def get_coaching_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get coaching events"""
    events = db.query(CoachingEvent).order_by(CoachingEvent.timestamp.desc()).limit(limit).all()
    return events


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
