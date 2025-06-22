"""
URLs para el servicio de cifrado de archivos
"""

from django.urls import path
from .views import (
    EncryptFileView,
    EncryptionInfoView,
    GenerateKeyView
)

urlpatterns = [
    # Endpoint principal para cifrar archivos
    path('encrypt/', EncryptFileView.as_view(), name='encrypt_file'),
    
    # Endpoint para obtener información del servicio
    path('info/', EncryptionInfoView.as_view(), name='encryption_info'),
    
    # Endpoint para generar nueva clave (solo desarrollo)
    path('generate-key/', GenerateKeyView.as_view(), name='generate_key'),
] 