import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from collections import namedtuple

from server.domain.services import request_service, owner_service, crane_model_service, user_repo
from server.domain.schemas import RequestCreate, RequestUpdate, RequestType, RequestStatus, UserRole
from server.domain.models import Request, User, Org, Crane, UserOrg, CraneModel

@pytest.fixture
def db_session_mock():
    return MagicMock(spec=Session)

class TestRequestService:
    def test_create_request_success(self, db_session_mock):
        # Arrange
        requester = User(id="user-sm-1", role=UserRole.SAFETY_MANAGER)
        request_in = RequestCreate(
            type=RequestType.CRANE_DEPLOY,
            requester_id=requester.id,
            target_entity_id="crane-1",
            related_entity_id="site-1",
        )

        with patch.object(user_repo, 'get', return_value=requester):
            with patch.object(db_session_mock, 'add'), patch.object(db_session_mock, 'commit'), patch.object(db_session_mock, 'refresh'):
                # Act
                result = request_service.create_request(db_session_mock, request_in)

                # Assert
                assert result is not None
                assert result.requester_id == requester.id
                assert result.status == RequestStatus.PENDING
                db_session_mock.add.assert_called_once()
                db_session_mock.commit.assert_called_once()
                db_session_mock.refresh.assert_called_once()

    def test_respond_to_request_approve_success(self, db_session_mock):
        # Arrange
        pending_request = Request(id="req-1", status=RequestStatus.PENDING)
        approver = User(id="user-owner-1", role=UserRole.OWNER)
        response_in = RequestUpdate(status=RequestStatus.APPROVED, approver_id=approver.id)

        db_session_mock.query.return_value.filter.return_value.first.return_value = pending_request
        with patch.object(user_repo, 'get', return_value=approver):
             with patch.object(db_session_mock, 'commit'), patch.object(db_session_mock, 'refresh'):
                # Act
                result = request_service.respond_to_request(db_session_mock, "req-1", response_in)

                # Assert
                assert result.status == RequestStatus.APPROVED
                assert result.approver_id == approver.id
                db_session_mock.commit.assert_called_once()
                db_session_mock.refresh.assert_called_once()

class TestOwnerService:
    def test_get_owners_with_stats(self, db_session_mock):
        # Arrange
        # The query returns a list of Row objects, which allow attribute access.
        # We can mimic this with a namedtuple.
        Row = namedtuple('Row', ['id', 'name', 'total_cranes', 'available_cranes'])
        mock_stats = [
            Row(id='org-1', name='Owner A', total_cranes=10, available_cranes=5),
            Row(id='org-2', name='Owner B', total_cranes=8, available_cranes=8),
        ]
        db_session_mock.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_stats

        # Act
        results = owner_service.get_owners_with_stats(db_session_mock)

        # Assert
        assert len(results) == 2
        assert results[0].name == 'Owner A'
        assert results[0].available_cranes == 5

    def test_get_my_requests(self, db_session_mock):
        # Arrange
        user_id = 'user-owner-1'
        owner_org_id = 'org-1'
        mock_user_org = UserOrg(user_id=user_id, org_id=owner_org_id)
        mock_requests = [Request(id='req-1'), Request(id='req-2')]

        db_session_mock.query.return_value.filter.return_value.first.return_value = mock_user_org
        db_session_mock.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = mock_requests

        # Act
        results = owner_service.get_my_requests(db_session_mock, user_id=user_id)

        # Assert
        assert len(results) == 2
        assert results[0].id == 'req-1'

class TestCraneModelService:
    def test_get_models(self, db_session_mock):
        # Arrange
        mock_models = [CraneModel(id='model-1', model_name='SS1926')]
        with patch('server.domain.repositories.crane_model_repo.get_multi', return_value=mock_models):
            # Act
            results = crane_model_service.get_models(db_session_mock)

            # Assert
            assert len(results) == 1
            assert results[0].model_name == 'SS1926'
