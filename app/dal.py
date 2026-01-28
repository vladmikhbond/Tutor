
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

# --------------------------- Tutor.db ------------------------

TUTOR_DB = "sqlite:////data/Tutor.db"

# Підтримка foreign keys для SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Створюємо engine 
engine = create_engine(
    TUTOR_DB,
    echo=True,
    connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency для роутерів
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------- Users.db ------------------------

engine_users = create_engine(
    "sqlite:////data/Users.db",
    echo=True,
    connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
)

# Створюємо фабрику сесій
SessionLocalUsers = sessionmaker(autocommit=False, autoflush=False, bind=engine_users)

# Dependency для роутерів
def get_users_db():
    db: Session = SessionLocalUsers()
    try:
        yield db
    finally:
        db.close()

# --------------------------- Attend.db ------------------------

engine_attend = create_engine(
    "sqlite:////data/Attend.db",
    echo=True,
    connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
)

# Створюємо фабрику сесій
SessionLocalAttend = sessionmaker(autocommit=False, autoflush=False, bind=engine_attend)

# Dependency для роутерів
def get_attend_db():
    db: Session = SessionLocalAttend()
    try:
        yield db
    finally:
        db.close()

# ================================================================

# from .models.attend_models import Base

# Base.metadata.create_all(engine_attend)