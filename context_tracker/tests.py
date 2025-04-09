from django.test import TestCase
from unittest.mock import patch, MagicMock
import jwt
from context_tracker.services.auth_service import AuthService
from context_tracker.models import APIKey
from context_tracker.services.context_service import ContextService
from context_tracker.models import ContextEntry
from context_tracker.services.workspace_service import WorkspaceService
from context_tracker.models import Workspace
from context_tracker.middleware import AuthenticationMiddleware
from django.http import HttpRequest, JsonResponse
from context_tracker.repositories.context_entry_repository import ContextEntryRepository
from context_tracker.repositories.workspace_repository import WorkspaceRepository
from context_tracker.models import User
import json
from rest_framework.test import APIClient
from rest_framework import status

class AuthServiceTestCase(TestCase):
    def setUp(self):
        self.auth_service = AuthService()

    @patch('jwt.decode')
    def test_validate_credentials_with_valid_token(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {'user_id': '123'}
        headers = {'Authorization': 'Bearer valid_token'}
        result = self.auth_service.validate_credentials(headers)
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['user_id'], '123')

    @patch('jwt.decode', side_effect=jwt.ExpiredSignatureError)
    def test_validate_credentials_with_expired_token(self, mock_jwt_decode):
        headers = {'Authorization': 'Bearer expired_token'}
        result = self.auth_service.validate_credentials(headers)
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['error'], 'Unauthorized: Token has expired')
        self.assertEqual(result['status'], 401)

    @patch('jwt.decode', side_effect=jwt.InvalidTokenError)
    def test_validate_credentials_with_invalid_token(self, mock_jwt_decode):
        headers = {'Authorization': 'Bearer invalid_token'}
        result = self.auth_service.validate_credentials(headers)
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['error'], 'Unauthorized: Invalid token')
        self.assertEqual(result['status'], 401)

    @patch.object(APIKey.objects, 'filter')
    def test_validate_credentials_with_valid_api_key(self, mock_filter):
        mock_filter.return_value.exists.return_value = True
        headers = {'X-API-KEY': 'valid_api_key'}
        result = self.auth_service.validate_credentials(headers)
        self.assertTrue(result['is_valid'])

    def test_validate_credentials_with_missing_credentials(self):
        headers = {}
        result = self.auth_service.validate_credentials(headers)
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['error'], 'Unauthorized: Missing credentials')
        self.assertEqual(result['status'], 401)

class ContextServiceTestCase(TestCase):
    def setUp(self):
        self.mock_context_entry_repo = MagicMock()
        self.mock_context_entry_repo.get_active_context.return_value = MagicMock(
            user_id='test_user', activity='Test Activity', note='Test Note', start_time='2025-04-07T12:00:00Z'
        )
        self.mock_context_entry_repo.create_context_entry.return_value = MagicMock(id='123')
        self.mock_context_entry_repo.end_active_contexts.return_value = 1
        self.context_service = ContextService(self.mock_context_entry_repo)
        self.user_id = 'test_user'

    @patch.object(ContextEntry.objects, 'filter')
    @patch.object(ContextEntry.objects, 'create')
    def test_log_user_context(self, mock_create, mock_filter):
        mock_filter.return_value.update.return_value = 1
        mock_create.return_value = MagicMock(id='123')

        result = self.context_service.log_user_context(self.user_id, 'Test Activity', 'Test Note')
        self.assertEqual(result['message'], 'Context logged')
        self.assertEqual(result['entry_id'], '123')

    @patch.object(ContextEntry.objects, 'filter')
    def test_stop_user_context_with_active_context(self, mock_filter):
        mock_filter.return_value.update.return_value = 1

        result = self.context_service.stop_user_context(self.user_id)
        self.assertEqual(result['message'], 'Context stopped')

    @patch.object(ContextEntry.objects, 'filter')
    def test_stop_user_context_without_active_context(self, mock_filter):
        self.mock_context_entry_repo.end_active_contexts.return_value = 0  # Ensure no active contexts are ended

        result = self.context_service.stop_user_context(self.user_id)
        self.assertEqual(result['message'], 'No active context to stop')
        self.assertEqual(result['status'], 400)

    @patch.object(ContextEntry.objects, 'filter')
    def test_get_user_status_with_active_context(self, mock_filter):
        mock_filter.return_value.first.return_value = MagicMock(
            user_id=self.user_id, activity='Test Activity', note='Test Note', start_time='2025-04-07T12:00:00Z'
        )

        result = self.context_service.get_user_status(self.user_id)
        self.assertEqual(result['user_id'], self.user_id)
        self.assertEqual(result['activity'], 'Test Activity')
        self.assertEqual(result['note'], 'Test Note')

    @patch.object(ContextEntry.objects, 'filter')
    def test_get_user_status_without_active_context(self, mock_filter):
        self.mock_context_entry_repo.get_active_context.return_value = None  # Ensure no active context is returned

        result = self.context_service.get_user_status(self.user_id)
        self.assertEqual(result['message'], 'No active context')
        self.assertEqual(result['status'], 404)

    @patch.object(ContextEntry.objects, 'filter')
    def test_get_user_entries(self, mock_filter):
        self.mock_context_entry_repo.get_all_contexts.return_value = [
            MagicMock(id='1', activity='Activity 1', note='Note 1', start_time='2025-04-07T12:00:00Z', end_time=None),
            MagicMock(id='2', activity='Activity 2', note='Note 2', start_time='2025-04-07T11:00:00Z', end_time='2025-04-07T11:30:00Z')
        ]

        result = self.context_service.get_user_entries(self.user_id)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['activity'], 'Activity 1')
        self.assertEqual(result[1]['end_time'], '2025-04-07T11:30:00Z')

class WorkspaceServiceTestCase(TestCase):
    def setUp(self):
        self.workspace_service = WorkspaceService()
        self.user = MagicMock()

    @patch.object(WorkspaceRepository, 'get_user_workspaces')
    def test_get_user_workspaces(self, mock_get_user_workspaces):
        mock_workspace1 = MagicMock()
        mock_workspace1.name = 'Workspace 1'
        mock_workspace2 = MagicMock()
        mock_workspace2.name = 'Workspace 2'
        mock_get_user_workspaces.return_value = [mock_workspace1, mock_workspace2]

        result = self.workspace_service.get_user_workspaces(self.user)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, 'Workspace 1')
        self.assertEqual(result[1].name, 'Workspace 2')

    @patch.object(Workspace.objects, 'filter')
    def test_join_workspace_success(self, mock_filter):
        mock_workspace = MagicMock()
        mock_workspace.members.add = MagicMock()  # Properly mock the add method
        mock_filter.return_value.first.return_value = mock_workspace

        result = self.workspace_service.join_workspace('workspace_id', self.user)
        self.assertEqual(result['message'], 'Joined workspace successfully')
        mock_workspace.members.add.assert_called_once_with(self.user)

    @patch.object(Workspace.objects, 'filter')
    def test_join_workspace_not_found(self, mock_filter):
        mock_filter.return_value.first.return_value = None

        result = self.workspace_service.join_workspace('invalid_workspace_id', self.user)
        self.assertEqual(result['error'], 'Workspace not found')
        self.assertEqual(result['status'], 404)

class AuthenticationMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = AuthenticationMiddleware(lambda req: JsonResponse({'message': 'Success'}))

    @patch('context_tracker.services.auth_service.AuthService.validate_credentials')
    def test_middleware_with_valid_credentials(self, mock_validate):
        mock_validate.return_value = {'is_valid': True, 'user_id': '123'}
        request = HttpRequest()
        request.path = '/log/'
        request.headers = {'Authorization': 'Bearer valid_token'}

        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Success'})
        self.assertEqual(request.user_id, '123')

    @patch('context_tracker.services.auth_service.AuthService.validate_credentials')
    def test_middleware_with_invalid_credentials(self, mock_validate):
        mock_validate.return_value = {'is_valid': False, 'error': 'Unauthorized: Invalid token', 'status': 401}
        request = HttpRequest()
        request.path = '/log/'
        request.headers = {'Authorization': 'Bearer invalid_token'}

        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(json.loads(response.content), {'error': 'Unauthorized: Invalid token'})

    def test_middleware_with_unprotected_route(self):
        request = HttpRequest()
        request.path = '/unprotected/'

        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Success'})

class ContextEntryRepositoryTestCase(TestCase):
    def setUp(self):
        self.repo = ContextEntryRepository()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.workspace = Workspace.objects.create(name='Test Workspace', owner=self.user)

    def test_create_context_entry(self):
        entry = self.repo.create_context_entry(self.user.id, 'Test Activity', 'Test Note')
        self.assertEqual(entry.activity, 'Test Activity')
        self.assertEqual(entry.note, 'Test Note')
        self.assertEqual(entry.user_id, self.user.id)

    def test_end_active_contexts(self):
        ContextEntry.objects.create(user=self.user, workspace=self.workspace, activity='Active Task')
        updated = self.repo.end_active_contexts(self.user.id)
        self.assertEqual(updated, 1)

    def test_get_active_context(self):
        entry = ContextEntry.objects.create(user=self.user, workspace=self.workspace, activity='Active Task')
        active_entry = self.repo.get_active_context(self.user.id)
        self.assertEqual(active_entry.id, entry.id)

    def test_get_all_contexts(self):
        ContextEntry.objects.create(user=self.user, workspace=self.workspace, activity='Task 1')
        ContextEntry.objects.create(user=self.user, workspace=self.workspace, activity='Task 2')
        entries = self.repo.get_all_contexts(self.user.id)
        self.assertEqual(len(entries), 2)

class WorkspaceRepositoryTestCase(TestCase):
    def setUp(self):
        self.repo = WorkspaceRepository()
        self.user = User.objects.create_user(username='testuser', password='password')

    @patch.object(Workspace.objects, 'filter')
    def test_get_user_workspaces(self, mock_filter):
        mock_filter.return_value.all.return_value = [
            MagicMock(id='1', name='Workspace 1'),
            MagicMock(id='2', name='Workspace 2')
        ]

        workspaces = self.repo.get_user_workspaces(self.user)
        self.assertEqual(len(workspaces), 2)
        self.assertEqual(workspaces[0].name, 'Workspace 1')
        self.assertEqual(workspaces[1].name, 'Workspace 2')

    def test_create_workspace(self):
        workspace = self.repo.create_workspace('Test Workspace', self.user)
        self.assertEqual(workspace.name, 'Test Workspace')
        self.assertEqual(workspace.owner, self.user)

    def test_get_workspace_by_id(self):
        workspace = Workspace.objects.create(name='Test Workspace', owner=self.user)
        fetched_workspace = self.repo.get_workspace_by_id(workspace.id)
        self.assertEqual(fetched_workspace.id, workspace.id)

    def test_add_member_to_workspace(self):
        workspace = Workspace.objects.create(name='Test Workspace', owner=self.user)
        new_user = User.objects.create_user(username='newuser', password='password')
        self.repo.add_member_to_workspace(workspace, new_user)
        self.assertIn(new_user, workspace.members.all())

    def test_get_user_workspaces(self):
        workspace1 = Workspace.objects.create(name='Workspace 1', owner=self.user)
        workspace2 = Workspace.objects.create(name='Workspace 2', owner=self.user)
        workspace1.members.add(self.user)
        workspace2.members.add(self.user)

        workspaces = self.repo.get_user_workspaces(self.user)
        self.assertEqual(len(workspaces), 2)
        self.assertEqual(workspaces[0].name, 'Workspace 1')
        self.assertEqual(workspaces[1].name, 'Workspace 2')

class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password", email="testuser@example.com")
        self.client.force_authenticate(user=self.user)

    def test_fetch_user(self):
        response = self.client.get("/user/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)

    def test_login(self):
        self.client.logout()
        response = self.client.post("/login/", {"email": "testuser@example.com", "password": "password"})  # Updated to use email
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_logout(self):
        response = self.client.post("/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful")

    def test_register(self):
        response = self.client.post("/register/", {
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User registered successfully")

from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

class CustomTokenObtainPairViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        self.login_url = "/login/"  # Updated to match the correct endpoint

    def test_login_with_email_success(self):
        data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "testuser@example.com")

    def test_login_with_email_invalid_password(self):
        data = {
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_login_with_nonexistent_email(self):
        data = {
            "email": "nonexistent@example.com",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)
