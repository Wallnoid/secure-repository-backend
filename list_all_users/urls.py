from django.urls import path
from .views import CognitoUserListView

urlpatterns = [
    path('cognito-users/', CognitoUserListView.as_view(), name='cognito-user-list'),
] 