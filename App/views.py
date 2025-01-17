# views.py
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from.serializers import LoginSerializer, RegisterOrganisationSerializers, RegisterUserSerializer, UserSerializer, OrganisationSerializer
from.models import User, Organisation
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User as p
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated


class RegisterUserView(APIView):
    def get(self, request):
        context = {
	        "firstName": "Enter First name",
	        "lastName": "Enter Last name",
	        "email": "Enter a valid email",
	        "password": "Enter password",
	        "phone": "Enter phone number",
        }
        return Response(context, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a User"""
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Creates an AbstractBaseUser
                AbstractBaseUser = p.objects.create_user(username=serializer.validated_data['email'], email=serializer.validated_data['email'], password=serializer.validated_data['password'])
                AbstractBaseUser.save()
                
                # Hash the password
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])

                # Creates a User profile (User Model)
                user = User(**serializer.validated_data)
                user.save()

                # Creates an default Organisation with User name   
                organisation = Organisation.objects.create(name=f"{user.firstName}'s Organisation", description='')
                organisation.users.add(user) # Add user to the organisation
                organisation.save() 

                # Assign AbstractBaseUser to User model, i.e the owner of the User Model. OnetoOnerelationship is estabilshed between AbstractBaseUser and User Model
                user.owner = AbstractBaseUser
                user.save()
                
                # Generate AccessToken for User 
                token = RefreshToken.for_user(AbstractBaseUser)
                
                return Response({'status': 'success', 'message': 'Registration successful', 'data': {'accessToken': str(token.access_token), 'user': UserSerializer(user).data}}, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({'status': 'Bad request', 'message': 'Registration unsuccessful', 'statusCode': 400}, status=status.HTTP_400_BAD_REQUEST)
            
        context = {
            "errors": serializer.errors
        }
        return Response(context, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        


@api_view(['POST', 'GET'])
def loginView(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                user_profile = User.objects.get(email=email)
                token = RefreshToken.for_user(user)
                context = {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        'accessToken': str(token.access_token),
                        'user': UserSerializer(user_profile).data
                    }
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {
                    "status": "error",
                    "message": "Authetication Failed",
                    'statusCode': 401
                }
                return Response(context, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        context = {
            'email': "Enter Your email",
            'password': "Enter your password"
        }
        return Response(context, status=status.HTTP_200_OK)



class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            REQUEST_USER = User.objects.get(email=request.user.email)
            LOOKUP_USER = User.objects.get(userId=pk)
            if REQUEST_USER == LOOKUP_USER:
                return Response({'status': 'success', 'message': 'User retrieved successfully', 'data': UserSerializer(LOOKUP_USER).data}, status=status.HTTP_200_OK)
            else:
                org = REQUEST_USER.user.all()
                print(org)
                user_in_same_org = User.objects.filter(user__in=org).exclude(userId=REQUEST_USER.userId)
                print(user_in_same_org)
                for n in user_in_same_org:
                    if n.userId == LOOKUP_USER.userId:
                        return Response({'status': 'success', 'message': 'User retrieved successfully', 'data': UserSerializer(n).data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'status': 'error', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrganisationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = User.objects.get(email=request.user)
        organisations = Organisation.objects.filter(users=user)
        return Response({'status': 'success', 'message': 'Organisations retrieved successfully', 'data':{
            'organisations': OrganisationSerializer(organisations, many=True).data
        } }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RegisterOrganisationSerializers(data=request.data)
        if serializer.is_valid():
                organisation = serializer.save()
                user = User.objects.get(email=request.user)
                organisation.users.add(user)
                return Response({'status': 'success', 'message': 'Organisation created successfully', 'data': OrganisationSerializer(organisation).data}, status=status.HTTP_201_CREATED)             
        else:
            return Response({'status': 'Bad Request', 'message': 'Client error', 'statusCode': 400, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
class OrganisationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            user = User.objects.get(owner=request.user)
            organisation = Organisation.objects.get(orgId=pk)
            if user in organisation.users.all():
                return Response({'status': 'success', 'message': 'Organisation retrieved successfully', 'data': OrganisationSerializer(organisation).data}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'error', 'message': 'You are not authorised to view this'}, status=status.HTTP_403_FORBIDDEN)
        
        except Organisation.DoesNotExist:
            return Response({'status': 'Bad request', 'message': 'Organisation does not exist', 'statusCode': 403}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({'status': 'Error', 'message': str(e), 'statusCode': 400}, status=status.HTTP_400_BAD_REQUEST)

class AddUserToOrganisationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        context = {
            'userId': "Enter a valid Id"
        }
        return Response(context, status=status.HTTP_200_OK)
    
   
    def post(self, request, pk):
        userId = request.data.get('userId')
        try:
            organisation = Organisation.objects.get(orgId=pk)
            user = get_object_or_404(User, userId=userId)
            print(user)
            if user:
                organisation.users.add(user)
                organisation.save()
                return Response({'status': 'success', 'message': 'User added to organisation successfully!'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Bad Request', 'message': 'Client error', 'statusCode': 400}, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            return Response({'status': 'Bad request', 'message': 'You do not have access to this organisation', 'statusCode': 403}, status=status.HTTP_403_FORBIDDEN)