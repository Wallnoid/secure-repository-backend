"""
URLs para el servicio de descifrado de archivos
"""

from django.urls import path
from .views import (
    DecryptFileView,
    ValidateEncryptedContentView,
    EstimateDecryptedSizeView,
    DecryptionInfoView,
    VerifyDecryptionServiceView
)

urlpatterns = [
    # Endpoint principal para descifrar archivos
    path('decrypt/', DecryptFileView.as_view(), name='decrypt_file'),
    
    # Endpoint para validar contenido cifrado sin descifrarlo
    path('validate/', ValidateEncryptedContentView.as_view(), name='validate_encrypted_content'),
    
    # Endpoint para estimar el tamaño descifrado
    path('estimate-size/', EstimateDecryptedSizeView.as_view(), name='estimate_decrypted_size'),
    
    # Endpoint para obtener información del servicio
    path('info/', DecryptionInfoView.as_view(), name='decryption_info'),
    
    # Endpoint para verificar el estado del servicio
    path('verify/', VerifyDecryptionServiceView.as_view(), name='verify_decryption_service'),
] 