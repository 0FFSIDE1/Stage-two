from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterUserSerializers, OrganisationSerializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.hashers import make_password
from .models import Organisation
# Create your views here.
class RegisterUser(APIView):
    def get(self, request):
        """Create a User"""
        context = {
	        "firstName": "Enter First name",
	        "lastName": "Enter Last name",
	        "email": "Enter a valid email",
	        "password": "Enter password",
	        "phone": "Enter phone number",
        }
        return Response(context, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RegisterUserSerializers(data=request.data)
        if serializer.is_valid():
            request_data = serializer.validated_data
            password = request_data['password']
            hash_password = make_password(password)
            request_data['password'] = hash_password
            user = User.objects.create_user(username=request_data['firstName'], email=request_data['email'], first_name=request_data['firstName'],password=hash_password)
            user.save()
            profile = serializer.save()
            org = Organisation.objects.create(name=f"{request_data['firstName']}'s Organisation")
            org.user.add(profile)
            org.save()
            token = RefreshToken.for_user(user)
            context = {
                'message': 'Registration successful',
                'data': {
                    'accessToken': str(token.access_token),
                    'user': serializer.data
                }
            }
            return Response(context, status=status.HTTP_201_CREATED)
        else:
            context = {
                "errors": serializer.errors
            }
            return Response(context, status=status.HTTP_422_UNPROCESSABLE_ENTITY)