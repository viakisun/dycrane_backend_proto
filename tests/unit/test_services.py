import pytest
import datetime as dt
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException

from server.domain.services import SiteService, UserService
from server.domain.schemas import SiteCreate, UserRole, SiteStatus
from server.domain.models import User, Site

@pytest.fixture
def db_session():
    """Provides a mock database session."""
    return MagicMock(spec=Session)

@pytest.fixture
def user_service():
    """Provides a mock user service."""
    return MagicMock(spec=UserService)

@pytest.fixture
def site_service(user_service):
    """Provides a SiteService instance with a mocked user_service."""
    return SiteService(user_service=user_service)

def test_create_site_success(site_service, user_service, db_session):
    """
    Tests successful site creation.
    """
    # Arrange
    site_in = SiteCreate(
        name="Test Site",
        address="123 Test St",
        start_date="2025-01-01",
        end_date="2025-12-31",
        requested_by_id="safety-manager-id"
    )
    mock_user = User(id="safety-manager-id", role=UserRole.SAFETY_MANAGER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    with patch('server.domain.repositories.site_repo.create', return_value=Site(**site_in.model_dump())) as mock_create:
        # Act
        result = site_service.create_site(db=db_session, site_in=site_in)

        # Assert
        user_service.get_user_and_validate_role.assert_called_once()
        mock_create.assert_called_once()
        assert result.name == site_in.name

def test_create_site_invalid_date(site_service, user_service, db_session):
    """
    Tests site creation with an invalid date range.
    """
    # Arrange
    site_in = SiteCreate(
        name="Test Site",
        start_date="2025-01-01",
        end_date="2025-12-31",
        requested_by_id="safety-manager-id"
    )
    site_in.end_date = dt.date(2024, 1, 1) # Invalid date
    mock_user = User(id="safety-manager-id", role=UserRole.SAFETY_MANAGER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        site_service.create_site(db=db_session, site_in=site_in)
    assert exc_info.value.status_code == 400
    assert "end_date must be after start_date" in str(exc_info.value.detail)

def test_approve_site_success(site_service, user_service, db_session):
    """
    Tests successful site approval.
    """
    # Arrange
    site_id = "site-id"
    approver_id = "manufacturer-id"
    mock_user = User(id=approver_id, role=UserRole.MANUFACTURER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    mock_site = Site(id=site_id, status=SiteStatus.PENDING_APPROVAL)

    with patch('server.domain.repositories.site_repo.get', return_value=mock_site) as mock_get, \
         patch('server.domain.repositories.site_repo.update') as mock_update:

        def update_side_effect(*args, **kwargs):
            db_obj = kwargs['db_obj']
            obj_in = kwargs['obj_in']
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            return db_obj

        mock_update.side_effect = update_side_effect

        # Act
        result = site_service.approve_site(db=db_session, site_id=site_id, approved_by_id=approver_id)

        # Assert
        assert mock_get.call_count == 1
        assert user_service.get_user_and_validate_role.call_count == 1
        mock_update.assert_called_once()
        assert result.status == SiteStatus.ACTIVE
        assert result.approved_by_id == approver_id

def test_approve_site_wrong_status(site_service, user_service, db_session):
    """
    Tests site approval when the site is not in PENDING_APPROVAL status.
    """
    # Arrange
    site_id = "site-id"
    approver_id = "manufacturer-id"
    mock_user = User(id=approver_id, role=UserRole.MANUFACTURER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    mock_site = Site(id=site_id, status=SiteStatus.ACTIVE)

    with patch('server.domain.repositories.site_repo.get', return_value=mock_site):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            site_service.approve_site(db=db_session, site_id=site_id, approved_by_id=approver_id)
        assert exc_info.value.status_code == 400
        assert "cannot approve" in str(exc_info.value.detail)
