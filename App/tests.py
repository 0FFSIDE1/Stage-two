from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User as AbstractUser
from django.utils import timezone
from datetime import timedelta
from .models import User, Organisation
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

class TokenGenerationTest(APITestCase):

    def setUp(self):
        self.user = AbstractUser.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.user_profile = User.objects.create(
            firstName='Test',
            lastName='User',
            email='test@example.com',
            password='password',
            owner=self.user
        )

    def test_token_generation(self):
        token = RefreshToken.for_user(self.user)
        self.assertIsNotNone(token)
        self.assertEqual(token['user_id'], str(self.user_profile.user_Id))

    def test_token_expiry(self):
        token = RefreshToken.for_user(self.user)
        expiry_time = token.access_token['exp']
        current_time = timezone.now()
        token_expiry_time = current_time + timedelta(minutes=5)  # Assuming the token expiry time is 5 minutes
        self.assertTrue(current_time.timestamp() < expiry_time < token_expiry_time.timestamp())





class OrganisationAccessTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = AbstractUser.objects.create_user(username='user1', email='user1@example.com', password='password')
        self.user2 = AbstractUser.objects.create_user(username='user2', email='user2@example.com', password='password')
        self.user1_profile = User.objects.create(
            firstName='User',
            lastName='One',
            email='user1@example.com',
            password='password',
            owner=self.user1
        )
        self.user2_profile = User.objects.create(
            firstName='User',
            lastName='Two',
            email='user2@example.com',
            password='password',
            owner=self.user2
        )
        self.org1 = Organisation.objects.create(name='Org1', description='Org1 Description')
        self.org1.users.add(self.user1_profile)

        self.org2 = Organisation.objects.create(name='Org2', description='Org2 Description')
        self.org2.users.add(self.user2_profile)

        self.client.login(username='user1@example.com', password='password')

    def test_organisation_data_access(self):
        response = self.client.get(reverse('organisation-detail', args=[self.org2.orgId]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You do not have access to this organisation')

class RegisterEndpointTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_successful_registration(self):
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "johndoe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['message'], 'Registration successful')

    def test_registration_with_existing_email(self):
        User.objects.create(
            firstName='Existing',
            lastName='User',
            email='existing@example.com',
            password='password',
            phone='1234567890'
        )
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "existing@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data['errors'], 'Email already exists')

    def test_registration_with_invalid_data(self):
        data = {
            "firstName": "",
            "lastName": "",
            "email": "invalidemail",
            "password": "",
            "phone": "123"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

