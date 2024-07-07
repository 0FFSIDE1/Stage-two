from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User as AbstractUser
from django.utils import timezone
from datetime import timedelta
from .models import User, Organisation
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe12@example.com',
            'password': 'password123',
            'phone': '212345679078'

        }
    
    def test_register_user_successfully(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertEqual(response.data['data']['user']['lastName'], 'Doe')

        org_name = f"{self.user_data['firstName']}'s Organisation"
        self.assertTrue(Organisation.objects.filter(name=org_name).exists())
    
    def test_login_user_successful(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.user_data['email'])
    
    def test_register_user_missing_fields(self):
        for field in ['firstName', 'lastName', 'email', 'password']:
            data =self.user_data.copy()
            data.pop(field)
            response = self.client.post(self.register_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertIn('errors', response.data)
        
    def test_register_user_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)