from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from .models import User, Organisation
from django.contrib.auth.models import User as p
from rest_framework import status
from django.conf import settings

class TokenGenerationTests(APITestCase):
    def setUp(self):
        self.user = p.objects.create_user(username="john.doe@example.com", email="john.doe@example.com", password="password123")
        self.user.save()

    def test_token_generation(self):
        token = RefreshToken.for_user(self.user)
        self.assertIn('exp', token.payload)
        self.assertIn('user_id', token.payload)
        self.assertEqual(token.payload['user_id'], self.user.user_Id)

    def test_token_expiration(self):
        token = RefreshToken.for_user(self.user)
        access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        expected_expiration = timezone.now() + access_token_lifetime
        
        # Assert that the token expires within the correct time range
        self.assertGreater(token.access_token.payload['exp'], timezone.now().timestamp())
        self.assertLessEqual(token.access_token.payload['exp'], (timezone.now() + access_token_lifetime).timestamp())

class OrganisationAccessControlTests(APITestCase):
    def setUp(self):
        self.user1 = p.objects.create_user(username="john.doe@example.com", password="password123")
        self.user2 = p.objects.create_user(username="jane.doe@example.com", password="password123")
        self.organisation1 = Organisation.objects.create(name="John's Organisation")
        self.organisation2 = Organisation.objects.create(name="Jane's Organisation")
        self.organisation1.users.add(self.user1)
        self.organisation2.users.add(self.user2)
        self.client.force_authenticate(user=self.user1)

    def test_user_cannot_access_other_organisation(self):
        url = reverse('organisation-detail', kwargs={'pk': self.organisation2.orgId})  # Replace with actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("message", response.data)
    
class RegisterEndpointTests(APITestCase):
    def test_register_user_success(self):
        url = reverse('register')  # Replace with the actual URL name
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("accessToken", response.data['data'])
        self.assertTrue(User.objects.filter(email="john.doe@example.com").exists())

    def test_register_user_validation_error(self):
        url = reverse('register')  # Replace with the actual URL name
        data = {
            "firstName": "",
            "lastName": "",
            "email": "invalid-email",
            "password": "",
            "phone": ""
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("errors", response.data)

    def test_register_user_database_constraints(self):
        url = reverse('register')  # Replace with the actual URL name
        p.objects.create_user(email="john.doe@example.com", password="password123")
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123",
            "phone": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)

