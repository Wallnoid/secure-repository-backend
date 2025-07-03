from django.urls import path
from .views import GenerateTOTPSecretView, ValidateTOTPView

urlpatterns = [
    path('generate/', GenerateTOTPSecretView.as_view(), name='generate_totp'),
    path('validate/', ValidateTOTPView.as_view(), name='validate_totp'),
] 