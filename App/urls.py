from django.urls import path
from .views import RegisterUser
urlpatterns = [
    path('auth/register', RegisterUser.as_view(), name='Register' ),
]
