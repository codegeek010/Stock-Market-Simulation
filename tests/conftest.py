import pytest
from sqlalchemy.orm import Session
from database.db import engine, Base
from tests.database import test_db_session


@pytest.fixture
def db_session():
    return next(test_db_session())


@pytest.fixture(scope="function", autouse=True)
def truncate_db(db_session):
    session = Session(bind=engine)
    session.begin_nested()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
        session.commit()
    yield
    session.rollback()
    session.close()
