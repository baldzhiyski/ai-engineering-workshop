from ..db.session import Base, engine
from ..db import models 


def init_db() -> None:
    Base.metadata.create_all(bind=engine)