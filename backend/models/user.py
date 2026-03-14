from sqlalchemy import Column, String, Boolean, DateTime
import uuid
from datetime import datetime
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_kyc_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
