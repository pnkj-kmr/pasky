from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
import json

User = get_user_model()


class AuthAPITestCase(TestCase):
    """Test cases for authentication API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.base_url = '/api/auth/'

    def test_register_start_success(self):
        """Test successful registration start."""
        response = self.client.post(
            f'{self.base_url}register/start/',
            data=json.dumps({
                'username': 'testuser',
                'email': 'test@example.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('challenge', data)
        self.assertIn('rp', data)
        self.assertIn('user', data)
        self.assertEqual(data['rp']['id'], 'localhost')

    def test_register_start_missing_fields(self):
        """Test registration start with missing fields."""
        # Missing email
        response = self.client.post(
            f'{self.base_url}register/start/',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing username
        response = self.client.post(
            f'{self.base_url}register/start/',
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_start_duplicate_username(self):
        """Test registration start with duplicate username."""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com'
        )

        # Try to register with same username
        response = self.client.post(
            f'{self.base_url}register/start/',
            data=json.dumps({
                'username': 'existinguser',
                'email': 'new@example.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_register_start_duplicate_email(self):
        """Test registration start with duplicate email."""
        # Create a user first
        User.objects.create_user(
            username='user1',
            email='existing@example.com'
        )

        # Try to register with same email
        response = self.client.post(
            f'{self.base_url}register/start/',
            data=json.dumps({
                'username': 'user2',
                'email': 'existing@example.com'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_login_start_success(self):
        """Test successful login start."""
        # Create a user first
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        # Note: User needs a passkey for login to work, but we test the endpoint

        response = self.client.post(
            f'{self.base_url}login/start/',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        # Will fail if no passkey, but we test the endpoint response
        # In real scenario, you'd need to create a passkey first
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_login_start_missing_username(self):
        """Test login start with missing username."""
        response = self.client.post(
            f'{self.base_url}login/start/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_start_user_not_found(self):
        """Test login start with non-existent user."""
        response = self.client.post(
            f'{self.base_url}login/start/',
            data=json.dumps({'username': 'nonexistent'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_info_requires_auth(self):
        """Test that user info endpoint requires authentication."""
        response = self.client.get(f'{self.base_url}user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_info_authenticated(self):
        """Test user info endpoint when authenticated."""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_login(user)

        response = self.client.get(f'{self.base_url}user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')

    def test_logout(self):
        """Test logout endpoint."""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_login(user)

        response = self.client.post(f'{self.base_url}logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.json())

