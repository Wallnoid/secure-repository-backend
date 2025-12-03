from django.urls import path
from .views import GenerateTOTPSecretView, ValidateTOTPView, SendTOTPQRView

urlpatterns = [
    path('generate/', GenerateTOTPSecretView.as_view(), name='generate_totp'),
    path('validate/', ValidateTOTPView.as_view(), name='validate_totp'),
    # path('send-qr/', SendTOTPQRView.as_view(), name='send_totp_qr'),
] 