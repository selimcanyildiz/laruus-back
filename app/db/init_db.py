from app.db.base import Base
from app.db.session import engine
from app.db.models import *  # noqa

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
