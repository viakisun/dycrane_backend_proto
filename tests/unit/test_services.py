import pytest
import datetime as dt
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException

from server.domain.services.site_service import SiteService
from server.domain.services.user_service import UserService
from server.domain.services.assignment_service import AssignmentService
from server.domain.schemas import SiteCreate, UserRole, SiteStatus, AssignCraneIn
from server.domain.models import User, Site, SiteCraneAssignment

@pytest.fixture
def assignment_service(user_service):
    """Provides an AssignmentService instance with a mocked user_service."""
    return AssignmentService(user_service=user_service)

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

from server.domain.schemas import SiteUpdate

def test_update_site_to_approve_success(site_service, user_service, db_session):
    """
    Tests successful site approval via the update method.
    """
    # Arrange
    site_id = "site-id"
    approver_id = "manufacturer-id"
    site_update = SiteUpdate(status=SiteStatus.ACTIVE, approved_by_id=approver_id)

    mock_user = User(id=approver_id, role=UserRole.MANUFACTURER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    mock_site = Site(id=site_id, status=SiteStatus.PENDING_APPROVAL)

    with patch('server.domain.repositories.site_repo.get', return_value=mock_site), \
         patch('server.domain.repositories.site_repo.update', side_effect=lambda db, db_obj, obj_in: db_obj) as mock_update:
        # Act
        result = site_service.update_site(db=db_session, site_id=site_id, site_in=site_update)

        # Assert
        user_service.get_user_and_validate_role.assert_called_once_with(
            db_session, user_id=approver_id, expected_role=UserRole.MANUFACTURER
        )
        mock_update.assert_called_once()
        # Check that the update payload passed to the repo contains the approval status
        update_payload = mock_update.call_args[1]['obj_in']
        assert update_payload['status'] == SiteStatus.ACTIVE
        assert update_payload['approved_by_id'] == approver_id
        assert 'approved_at' in update_payload


def test_update_site_to_approve_wrong_status(site_service, user_service, db_session):
    """
    Tests site approval when the site is not in PENDING_APPROVAL status.
    """
    # Arrange
    site_id = "site-id"
    approver_id = "manufacturer-id"
    site_update = SiteUpdate(status=SiteStatus.ACTIVE, approved_by_id=approver_id)

    mock_user = User(id=approver_id, role=UserRole.MANUFACTURER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    mock_site = Site(id=site_id, status=SiteStatus.ACTIVE)

    with patch('server.domain.repositories.site_repo.get', return_value=mock_site):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            site_service.update_site(db=db_session, site_id=site_id, site_in=site_update)
        assert exc_info.value.status_code == 400
        assert "cannot approve" in str(exc_info.value.detail)

def test_assign_crane_to_site_conflict(assignment_service, user_service, db_session):
    """
    Tests crane assignment when the crane is already assigned during the requested period.
    """
    # Arrange
    assignment_in = AssignCraneIn(
        site_id="site-1",
        crane_id="crane-1",
        safety_manager_id="sm-1",
        start_date=dt.date(2025, 1, 10),
        end_date=dt.date(2025, 1, 20),
    )
    mock_user = User(id="sm-1", role=UserRole.SAFETY_MANAGER, is_active=True)
    user_service.get_user_and_validate_role.return_value = mock_user

    # Mock an existing, overlapping assignment
    existing_assignment = SiteCraneAssignment(
        id="as-1",
        crane_id="crane-1",
        site_id="site-0",
        start_date=dt.date(2025, 1, 15),
        end_date=dt.date(2025, 1, 25),
    )

    # Configure the mock query to return the overlapping assignment
    db_session.query.return_value.filter.return_value.first.return_value = existing_assignment

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        assignment_service.assign_crane_to_site(db=db_session, assignment_in=assignment_in)

    assert exc_info.value.status_code == 409
    assert "already assigned" in str(exc_info.value.detail)
