from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./finops_optimizer.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class OrphanedResource(Base):
    __tablename__ = "orphaned_resources"

    id = Column(Integer, primary_key=True, index=True)
    cloud_provider = Column(String, nullable=False) # 'AWS' or 'Azure'
    resource_id = Column(String, unique=True, nullable=False)
    resource_type = Column(String, nullable=False)   # 'volume', 'vm', etc.
    region = Column(String, nullable=False)
    estimated_monthly_waste = Column(Float, default=0.0)
    status = Column(String, default="Detected")     # Detected, Remediated
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)