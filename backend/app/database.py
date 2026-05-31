import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DATA_DIR = Path.home() / ".tab-manager"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "workspace.db"
PROJECT_DB_PATH = PROJECT_DATA_DIR / "workspace.db"


def get_database_url() -> str:
    override = os.environ.get("TAB_MANAGER_DB_PATH")
    if override:
        db_path = Path(override).expanduser()
    elif os.environ.get("TAB_MANAGER_USE_HOME") == "1":
        db_path = DEFAULT_DB_PATH
    else:
        db_path = PROJECT_DB_PATH

    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
