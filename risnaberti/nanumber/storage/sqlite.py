# nanumber/storage/sqlite.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from .base import BaseStorage
import threading
from datetime import datetime

Base = declarative_base()

class AutoNumber(Base):
    __tablename__ = "auto_numbers"
    key = Column(String, primary_key=True)
    last_value = Column(Integer, nullable=False, default=0)
    last_reset_year = Column(Integer, nullable=False, default=datetime.now().year)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SQLiteStorage(BaseStorage):
    def __init__(self, db_url="sqlite:///nanumber.db"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self._lock = threading.Lock()

    def get_last_number(self, key: str) -> int:
        with self.Session() as session:
            rec = session.query(AutoNumber).filter_by(key=key).first()
            return rec.last_value if rec else 0

    def increment(self, key: str) -> int:
        current_year = datetime.now().year
        with self._lock, self.Session() as session:
            session.expire_all()
            rec = session.query(AutoNumber).filter_by(key=key).first()
            if not rec:
                rec = AutoNumber(key=key, last_value=1, last_reset_year=current_year)
                session.add(rec)
                session.commit()
                return 1
            if rec.last_reset_year != current_year:
                rec.last_value = 1
                rec.last_reset_year = current_year
            else:
                rec.last_value += 1
            session.commit()
            return rec.last_value

    def reset(self, key: str, value: int = 0):
        with self.Session() as session:
            rec = session.query(AutoNumber).filter_by(key=key).first()
            if rec:
                rec.last_value = value
                rec.last_reset_year = datetime.now().year
            else:
                rec = AutoNumber(key=key, last_value=value, last_reset_year=datetime.now().year)
                session.add(rec)
            session.commit()
