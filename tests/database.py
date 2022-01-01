from sqlalchemy.orm import Session

from database.db import engine


def test_db_session():
    session = Session(bind=engine)
    try:
        yield session
        session.rollback()
    finally:
        session.close()
