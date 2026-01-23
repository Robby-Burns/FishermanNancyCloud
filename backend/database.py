from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from backend.config import settings
from backend.security import encrypt_value, decrypt_value
import os

Base = declarative_base()

class EncryptedString(TypeDecorator):
    """Encrypted string column"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_value(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_value(value)
        return value

class Catch(Base):
    """Logged catches"""
    __tablename__ = "catches"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    fish_type = Column(String, nullable=False)  # Crab, Salmon, Halibut, Other
    pounds = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="catch")
    sales = relationship("Sale", back_populates="catch")


class Buyer(Base):
    """Buyer contacts - PII is encrypted"""
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(EncryptedString, nullable=False)  # Encrypted
    carrier = Column(String, nullable=False)  # verizon, att, tmobile, sprint
    email = Column(EncryptedString, nullable=True) # Encrypted
    preferred_fish = Column(String, nullable=True)  # Comma-separated: "Crab, Salmon"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="buyer")
    sales = relationship("Sale", back_populates="buyer")


class Price(Base):
    """Cannery prices"""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    fish_type = Column(String, nullable=False)
    price_per_lb = Column(Float, nullable=False)
    cannery_name = Column(String, nullable=False, default="Westport Cannery")
    cannery_url = Column(String, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    """Messages sent to buyers"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    catch_id = Column(Integer, ForeignKey("catches.id"), nullable=True)
    message_text = Column(Text, nullable=False)
    sent_at = Column(DateTime, nullable=True)  # Null if draft
    status = Column(String, default="draft")  # draft, sent, failed
    
    # Relationships
    buyer = relationship("Buyer", back_populates="messages")
    catch = relationship("Catch", back_populates="messages")


class CoachingEvent(Base):
    """Universal Coach violations and coaching"""
    __tablename__ = "coaching_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_id = Column(String, nullable=False, default="fishing_agent_001")
    agent_type = Column(String, nullable=False, default="SALES_COORDINATOR")
    guardrail = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # critical, high, medium, low, info
    violation_description = Column(Text, nullable=False)
    coaching_delivered = Column(Text, nullable=False)
    coaching_depth = Column(String, nullable=False)
    agent_response = Column(Text, nullable=True)
    improved = Column(Boolean, nullable=True)
    improvement_timeline = Column(Integer, nullable=True)


class Sale(Base):
    """Completed sales (logged manually by fisherman)"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    catch_id = Column(Integer, ForeignKey("catches.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=False)
    pounds_sold = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)  # Total price, not per lb
    meetup_details = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    catch = relationship("Catch", back_populates="sales")
    buyer = relationship("Buyer", back_populates="sales")


class Cannery(Base):
    """Cannery websites for price scraping"""
    __tablename__ = "canneries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
def get_engine():
    """Create database engine"""
    
    # Check if using Postgres (Neon)
    if settings.database_url.startswith("postgres"):
        engine = create_engine(
            settings.database_url,
            echo=False
        )
    else:
        # Fallback to SQLite
        os.makedirs("data", exist_ok=True)
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
    
    return engine


def init_db():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db():
    """Get database session"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
