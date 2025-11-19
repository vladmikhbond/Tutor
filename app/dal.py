
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy import event
from sqlalchemy.engine import Engine

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

# # ================================================================
# TSS_DB = "sqlite:////data/PSS.db"

# engine_pss = create_engine(
#     TSS_DB,
#     echo=True,
#     connect_args={"check_same_thread": False}  # потрібно для SQLite + багатопоточного доступу
# )

# SessionLocalPss = sessionmaker(autocommit=False, autoflush=False, bind=engine_pss)

# def get_db_pss():
#     db: Session = SessionLocalPss()
#     try:
#         yield db
#     finally:
#         db.close()

# ================================================================

# from models.models import Base
# if __name__ == "__main__":
#     Base.metadata.create_all(engine)

