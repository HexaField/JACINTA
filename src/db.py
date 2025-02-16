# src/db.py
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import json


# SQLite database URL (the file "tasks.db" will be created in the project root)
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# Create the SQLAlchemy engine (with check_same_thread set for SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class and a SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions.
Base = declarative_base()

# Define the Task model (table)
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, default="")  # New description field
    status = Column(String, index=True)  # e.g., "pending", "current", "completed"

    jobs = Column(Text, default="[]")  # Store sub-tasks as JSON

    def get_jobs(self):
        return json.loads(self.jobs) if self.jobs else []

    def set_jobs(self, jobs_list):
        self.jobs = json.dumps(jobs_list)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def init_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)
