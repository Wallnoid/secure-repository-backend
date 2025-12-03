"""
Vistas para el servicio de cifrado de archivos binarios
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .encryption_service import FileEncryptionService
from .serializers import (
    EncryptFileSerializer,
    EncryptionResponseSerializer,
    EncryptionInfoSerializer,
    ErrorResponseSerializer
)


class EncryptFileView(APIView):
    """
    Vista para cifrar archivos binarios (.bin) usando AES 128 implementado desde cero
    """
    parser_classes = (MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_description="Cifrar archivo .bin usando AES 128 personalizado. Recibe un archivo .bin y retorna un archivo .bin cifrado.",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="Archivo .bin a cifrar",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                description="Descripción del archivo (opcional)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: EncryptionResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer
        },
        consumes=['multipart/form-data'],
        tags=['Binary Encryption']
    )
    def post(self, request):
        """
        Endpoint para cifrar un archivo .bin completo
        Retorna un archivo .bin cifrado listo para almacenar en base de datos
        """
        try:
            # Validar datos de entrada
            serializer = EncryptFileSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'message': 'Datos de entrada inválidos. El archivo debe ser .bin',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener datos validados
            validated_data = serializer.validated_data
            uploaded_file = validated_data['file']
            
            # Preparar metadatos
            metadata = {}
            if 'description' in validated_data:
                metadata['description'] = validated_data['description']
            
            # Inicializar servicio de cifrado
            encryption_service = FileEncryptionService()
            
            # Cifrar el archivo
            result = encryption_service.encrypt_file(
                uploaded_file=uploaded_file,
                metadata=metadata if metadata else None
            )
            
            if result['status'] == 'error':
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': f'Error de configuración: {str(e)}',
                'error_code': 'CONFIG_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}',
                'error_code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EncryptionInfoView(APIView):
    """
    Vista para obtener información sobre el servicio de cifrado de archivos binarios
    """
    
    @swagger_auto_schema(
        operation_description="Obtener información sobre el algoritmo de cifrado utilizado para archivos .bin",
        responses={
            200: EncryptionInfoSerializer,
        },
        tags=['Binary Encryption']
    )
    def get(self, request):
        """
        Endpoint para obtener información del servicio de cifrado binario
        """
        try:
            encryption_service = FileEncryptionService()
            info = encryption_service.get_encryption_info()
            
            return Response(info, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al obtener información: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateKeyView(APIView):
    """
    Vista para generar una nueva clave AES 128 (solo para desarrollo/testing)
    """
    
    @swagger_auto_schema(
        operation_description="Generar una nueva clave AES 128 segura (solo para desarrollo)",
        responses={
            200: openapi.Response(
                description="Clave generada exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'key': openapi.Schema(type=openapi.TYPE_STRING, description="Nueva clave AES 128"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje informativo"),
                        'warning': openapi.Schema(type=openapi.TYPE_STRING, description="Advertencia de seguridad")
                    }
                )
            )
        },
        tags=['Utilities']
    )
    def get(self, request):
        """
        Endpoint para generar una nueva clave AES 128
        NOTA: Este endpoint es solo para desarrollo/testing
        """
        try:
            new_key = FileEncryptionService.generate_aes_key()
            
            return Response({
                'key': new_key,
                'message': 'Nueva clave AES 128 generada exitosamente',
                'warning': 'Esta clave debe almacenarse de forma segura en las variables de entorno'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al generar clave: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
