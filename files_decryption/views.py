"""
Vistas para el servicio de descifrado de archivos binarios
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .decryption_service import FileDecryptionService
from .serializers import (
    DecryptFileSerializer,
    ValidateEncryptedContentSerializer,
    EstimateSizeSerializer,
    DecryptionResponseSerializer,
    ValidationResponseSerializer,
    SizeEstimationResponseSerializer,
    DecryptionInfoSerializer,
    VerificationResponseSerializer,
    ErrorResponseSerializer
)


class DecryptFileView(APIView):
    """
    Vista para descifrar archivos binarios (.bin) usando AES 128 implementado desde cero
    """
    parser_classes = (MultiPartParser, FormParser)
    
    @swagger_auto_schema(
        operation_description="Descifrar archivo .bin cifrado usando AES 128 personalizado. Recibe un archivo .bin cifrado y retorna un archivo .bin descifrado.",
        manual_parameters=[
            openapi.Parameter(
                'encrypted_file',
                openapi.IN_FORM,
                description="Archivo .bin cifrado a descifrar",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'additional_info',
                openapi.IN_FORM,
                description="Información adicional sobre el archivo cifrado (opcional, formato JSON)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: DecryptionResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer
        },
        consumes=['multipart/form-data'],
        tags=['Binary Decryption']
    )
    def post(self, request):
        """
        Endpoint para descifrar archivo .bin cifrado
        Retorna un archivo .bin descifrado listo para uso
        """
        try:
            # Validar datos de entrada
            serializer = DecryptFileSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'message': 'Datos de entrada inválidos. El archivo debe ser .bin',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener datos validados
            validated_data = serializer.validated_data
            encrypted_file = validated_data['encrypted_file']
            additional_info = validated_data.get('additional_info', None)
            
            # Inicializar servicio de descifrado
            decryption_service = FileDecryptionService()
            
            # Descifrar el archivo
            result = decryption_service.decrypt_file(
                uploaded_file=encrypted_file,
                additional_info=additional_info
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


class ValidateEncryptedContentView(APIView):
    """
    Vista para validar contenido cifrado sin descifrarlo
    """
    
    @swagger_auto_schema(
        operation_description="Validar formato de contenido cifrado sin descifrarlo",
        request_body=ValidateEncryptedContentSerializer,
        responses={
            200: ValidationResponseSerializer,
            400: ErrorResponseSerializer
        },
        tags=['Decryption']
    )
    def post(self, request):
        """
        Endpoint para validar contenido cifrado
        """
        try:
            # Validar datos de entrada
            serializer = ValidateEncryptedContentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'message': 'Datos de entrada inválidos',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener datos validados
            validated_data = serializer.validated_data
            encrypted_content = validated_data['encrypted_content']
            
            # Inicializar servicio de descifrado
            decryption_service = FileDecryptionService()
            
            # Validar contenido
            is_valid = decryption_service.validate_encrypted_content(encrypted_content)
            
            # Obtener detalles del formato
            format_details = {}
            if is_valid:
                import base64
                encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
                format_details = {
                    'encrypted_size_bytes': len(encrypted_bytes),
                    'encrypted_size_base64': len(encrypted_content),
                    'total_blocks': len(encrypted_bytes) // 16,
                    'format': 'base64',
                    'block_size': 16
                }
            
            result = {
                'is_valid': is_valid,
                'status': 'validated' if is_valid else 'invalid',
                'message': 'Contenido válido para descifrado' if is_valid else 'Contenido cifrado inválido',
                'format_details': format_details if is_valid else None
            }
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al validar contenido: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EstimateDecryptedSizeView(APIView):
    """
    Vista para estimar el tamaño del contenido descifrado
    """
    
    @swagger_auto_schema(
        operation_description="Estimar el tamaño del contenido descifrado sin descifrarlo",
        request_body=EstimateSizeSerializer,
        responses={
            200: SizeEstimationResponseSerializer,
            400: ErrorResponseSerializer
        },
        tags=['Decryption']
    )
    def post(self, request):
        """
        Endpoint para estimar tamaño descifrado
        """
        try:
            # Validar datos de entrada
            serializer = EstimateSizeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'message': 'Datos de entrada inválidos',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener datos validados
            validated_data = serializer.validated_data
            encrypted_content = validated_data['encrypted_content']
            
            # Inicializar servicio de descifrado
            decryption_service = FileDecryptionService()
            
            # Estimar tamaño
            result = decryption_service.estimate_decrypted_size(encrypted_content)
            
            if result.get('status') == 'error':
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al estimar tamaño: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DecryptionInfoView(APIView):
    """
    Vista para obtener información sobre el servicio de descifrado de archivos binarios
    """
    
    @swagger_auto_schema(
        operation_description="Obtener información sobre el algoritmo de descifrado utilizado para archivos .bin",
        responses={
            200: DecryptionInfoSerializer,
        },
        tags=['Binary Decryption']
    )
    def get(self, request):
        """
        Endpoint para obtener información del servicio de descifrado binario
        """
        try:
            decryption_service = FileDecryptionService()
            info = decryption_service.get_decryption_info()
            
            return Response(info, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error al obtener información: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyDecryptionServiceView(APIView):
    """
    Vista para verificar que el servicio de descifrado está funcionando
    """
    
    @swagger_auto_schema(
        operation_description="Verificar que el servicio de descifrado está operativo",
        responses={
            200: VerificationResponseSerializer,
            500: ErrorResponseSerializer
        },
        tags=['Decryption']
    )
    def get(self, request):
        """
        Endpoint para verificar el estado del servicio de descifrado
        """
        try:
            decryption_service = FileDecryptionService()
            verification_result = decryption_service.verify_decryption_capability()
            
            return Response(verification_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error en la verificación del servicio: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
