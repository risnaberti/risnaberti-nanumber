# risnaberti/nanumber/storage/sqlalchemy_storage.py
from sqlalchemy import (
    create_engine, Column, String, Integer, DateTime, func, select, text
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, ProgrammingError
from contextlib import contextmanager
from datetime import datetime
import threading

from .base import BaseStorage

Base = declarative_base()


class AutoNumber(Base):
    """Database model for storing auto-number sequences."""
    __tablename__ = "auto_numbers"

    key = Column(String(100), primary_key=True)
    last_value = Column(Integer, nullable=False, default=0)
    last_reset_year = Column(Integer, nullable=False, default=datetime.now().year)
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )


class SQLAlchemyStorage(BaseStorage):
    """
    Universal SQLAlchemy-based storage for Nanumber.
    
    Supports: PostgreSQL, MySQL, SQLite, and other SQLAlchemy-compatible databases.
    Uses transactions and row-level locking (FOR UPDATE) for thread/process safety.
    
    Args:
        db_url: SQLAlchemy database URL
            Examples:
            - "sqlite:///nanumber.db"
            - "postgresql://user:pass@localhost/dbname"
            - "mysql+pymysql://user:pass@localhost/dbname"
    
    Example:
        >>> storage = SQLAlchemyStorage("sqlite:///nanumber.db")
        >>> gen = NumberGenerator(storage)
    """

    def __init__(self, db_url: str = "sqlite:///nanumber.db"):
        self.engine = create_engine(
            db_url, 
            pool_pre_ping=True,  # Verify connections before use
            future=True
        )
        
        # Create tables if not exist
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine, autoflush=False)
        self._lock = threading.Lock()
        self._dialect = self.engine.url.get_backend_name().lower()

    @contextmanager
    def _session_scope(self):
        """Provide a transactional scope around operations."""
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
        """Get last generated number for given key."""
        with self._session_scope() as session:
            rec = session.get(AutoNumber, key)
            return rec.last_value if rec else 0

    def increment(self, key: str) -> int:
        """
        Atomically increment and return next number for given key.
        Automatically resets to 1 when year changes.
        """
        current_year = datetime.now().year

        # Thread-level lock for SQLite, DB-level lock for others
        with self._lock if self._dialect == "sqlite" else self._session_scope() as session:
            if self._dialect == "sqlite":
                # SQLite: use thread lock + regular session
                with self._session_scope() as session:
                    rec = session.get(AutoNumber, key)
            else:
                # PostgreSQL/MySQL: use SELECT FOR UPDATE
                try:
                    stmt = select(AutoNumber).where(
                        AutoNumber.key == key
                    ).with_for_update()
                    rec = session.execute(stmt).scalars().one_or_none()
                except (OperationalError, ProgrammingError):
                    # Fallback if FOR UPDATE not supported
                    rec = session.get(AutoNumber, key)

            # Create new record if doesn't exist
            if not rec:
                rec = AutoNumber(
                    key=key, 
                    last_value=1, 
                    last_reset_year=current_year
                )
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
        """Reset number sequence for given key to specified value."""
        with self._session_scope() as session:
            rec = session.get(AutoNumber, key)
            
            if rec:
                rec.last_value = value
                rec.last_reset_year = datetime.now().year
            else:
                rec = AutoNumber(
                    key=key, 
                    last_value=value, 
                    last_reset_year=datetime.now().year
                )
                session.add(rec)