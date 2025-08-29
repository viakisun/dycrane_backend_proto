import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from server.domain.models import Base, Site, User, UserRole
from server.domain.repositories import site_repo, user_repo
from server.domain.schemas import SiteCreate, UserCreate

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Creates a new database session for a test.
    """
    # Set schema to None for all tables for SQLite compatibility
    for table in Base.metadata.tables.values():
        table.schema = None
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_site(db_session: Session):
    # Arrange
    site_in = SiteCreate(
        name="Test Site",
        address="123 Test St",
        start_date="2025-01-01",
        end_date="2025-12-31",
        requested_by_id="user1"
    )
    # We need to create the user first to satisfy the foreign key constraint
    user = User(id="user1", name="Test User", email="test@test.com", role=UserRole.SAFETY_MANAGER, is_active=True, hashed_password="password")
    db_session.add(user)
    db_session.commit()

    # Act
    created_site = site_repo.create(db=db_session, obj_in=site_in)

    # Assert
    assert created_site.id is not None
    assert created_site.name == site_in.name
    assert db_session.query(Site).count() == 1

def test_get_site(db_session: Session):
    # Arrange
    user = User(id="user1", name="Test User", email="test@test.com", role=UserRole.SAFETY_MANAGER, is_active=True, hashed_password="password")
    db_session.add(user)
    db_session.commit()
    site_in = SiteCreate(
        name="Test Site",
        start_date="2025-01-01",
        end_date="2025-12-31",
        requested_by_id="user1"
    )
    created_site = site_repo.create(db=db_session, obj_in=site_in)

    # Act
    retrieved_site = site_repo.get(db=db_session, id=created_site.id)

    # Assert
    assert retrieved_site is not None
    assert retrieved_site.id == created_site.id
    assert retrieved_site.name == created_site.name

def test_create_user(db_session: Session):
    # Arrange
    user_in = UserCreate(
        email="test@example.com",
        password="password",
        name="Test User",
        role=UserRole.DRIVER
    )

    # Act
    created_user = user_repo.create(db=db_session, obj_in=user_in)

    # Assert
    assert created_user.id is not None
    assert created_user.email == user_in.email
    assert db_session.query(User).count() == 1

def test_get_user_by_email(db_session: Session):
    # Arrange
    user_in = UserCreate(
        email="test@example.com",
        password="password",
        name="Test User",
        role=UserRole.DRIVER
    )
    user_repo.create(db=db_session, obj_in=user_in)

    # Act
    retrieved_user = user_repo.get_by_email(db=db_session, email="test@example.com")

    # Assert
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"
