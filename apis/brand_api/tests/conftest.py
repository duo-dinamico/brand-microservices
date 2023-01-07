import pytest
from fastapi.testclient import TestClient

from ..db.database import Base, SessionLocal, engine
from ..main import app

client = TestClient(app)


@pytest.fixture
def db_session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    Base.metadata.drop_all(engine)
    session.close()
