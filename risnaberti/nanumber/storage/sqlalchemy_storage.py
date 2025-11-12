# nanumber/storage/sqlalchemy_storage.py
from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, func, select, text
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, NoResultFound, ProgrammingError
from contextlib import contextmanager
from datetime import datetime
import threading
import os

from .base import BaseStorage

Base = declarative_base()

class AutoNumber(Base):
    __tablename__ = "auto_numbers"

    key = Column(String(100), primary_key=True)
    last_value = Column(Integer, nullable=False, default=0)
    last_reset_year = Column(Integer, nullable=False, default=datetime.now().year)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SQLAlchemyStorage(BaseStorage):
    """
    Universal SQLAlchemy-based storage for Nanumber.
    Supports PostgreSQL, MySQL, SQLite, and others.
    Uses transaction + FOR UPDATE (if supported) to ensure atomic increments.
    """

    def __init__(self, db_url="sqlite:///nanumber.db"):
        self.engine = create_engine(db_url, pool_pre_ping=True, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False)
        self._lock = threading.Lock()
        self._dialect = self.engine.url.get_backend_name().lower()

    @contextmanager
    def _session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_last_number(self, key: str) -> int:
        with self._session_scope() as session:
            rec = session.get(AutoNumber, key)
            return rec.last_value if rec else 0

    def increment(self, key: str) -> int:
        current_year = datetime.now().year

        # Thread-level lock to prevent concurrent access within same process
        with self._lock, self._session_scope() as session:
            try:
                # Try to acquire row-level lock if supported
                if self._dialect not in ["sqlite"]:
                    stmt = select(AutoNumber).where(AutoNumber.key == key).with_for_update()
                    rec = session.execute(stmt).scalars().one_or_none()
                else:
                    # SQLite fallback (no row-level lock)
                    rec = session.get(AutoNumber, key)
            except (OperationalError, ProgrammingError):
                # fallback if FOR UPDATE not supported
                rec = session.get(AutoNumber, key)

            # Create if not exists
            if not rec:
                rec = AutoNumber(key=key, last_value=1, last_reset_year=current_year)
                session.add(rec)
                return 1

            # Reset counter if year changed
            if rec.last_reset_year != current_year:
                rec.last_value = 1
                rec.last_reset_year = current_year
            else:
                rec.last_value += 1

            return rec.last_value

    def reset(self, key: str, value: int = 0):
        with self._session_scope() as session:
            rec = session.get(AutoNumber, key)
            if rec:
                rec.last_value = value
                rec.last_reset_year = datetime.now().year
            else:
                rec = AutoNumber(
                    key=key, last_value=value, last_reset_year=datetime.now().year
                )
                session.add(rec)
