from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.models import *  # noqa
from app.core.parameters import seed_parameters


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_parameters(db)
    finally:
        db.close()
