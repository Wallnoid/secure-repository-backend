from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime

from audit.services import AuditService
from audit.serializers import (
    FileAuditRequestSerializer, 
    FileAuditResponseSerializer,
    AllFilesAuditResponseSerializer
)

# Instanciar el servicio
audit_service = AuditService()


class FileAuditView(APIView):

    
    @swagger_auto_schema(
        operation_description="Obtiene información de auditoría de un archivo específico combinando datos de S3 y base de datos",
        query_serializer=FileAuditRequestSerializer,
        responses={
            200: FileAuditResponseSerializer,
            400: openapi.Response(description="Error en la solicitud"),
            404: openapi.Response(description="Archivo no encontrado"),
            500: openapi.Response(description="Error interno del servidor")
        },
        tags=['Auditoría']
    )
    def get(self, request):
        try:
            # Validar parámetros de entrada
            serializer = FileAuditRequestSerializer(data=request.query_params)
            if not serializer.is_valid():
                return Response(
                    {"error": "INVALID_PARAMETERS", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            file_key = serializer.validated_data['file_key']
            
            user_id = getattr(request.user, 'username', None)
            user_email = getattr(request.user, 'email', None)
            
            # Obtener información de auditoría
            audit_info = audit_service.get_file_audit_info(file_key, user_id, user_email)
            
            # Manejar diferentes tipos de errores
            if 'error' in audit_info:
                error_type = audit_info['error']
                
                if error_type == 'FILE_NOT_FOUND':
                    return Response(audit_info, status=status.HTTP_404_NOT_FOUND)
                elif error_type == 'S3_ACCESS_ERROR':
                    return Response(audit_info, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return Response(audit_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response(audit_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "error": "UNEXPECTED_ERROR",
                    "message": f"Error inesperado en el servidor: {str(e)}",
                    "audit_timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AllFilesAuditView(APIView):
    
    @swagger_auto_schema(
        operation_description="Obtiene información de auditoría de todos los archivos en el bucket del usuario",
        responses={
            200: AllFilesAuditResponseSerializer,
            400: openapi.Response(description="Error en la solicitud"),
            500: openapi.Response(description="Error interno del servidor")
        },
        tags=['Auditoría']
    )
    def get(self, request):
        try:
            user_id = getattr(request.user, 'username', None)
            user_email = getattr(request.user, 'email', None)
            
            # Obtener información de auditoría de todos los archivos
            audit_results = audit_service.get_all_files_audit(user_id, user_email)
            
            # Manejar diferentes tipos de errores
            if 'error' in audit_results:
                error_type = audit_results['error']
                
                if error_type in ['BUCKET_ACCESS_ERROR', 'BUCKET_LIST_ERROR']:
                    return Response(audit_results, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return Response(audit_results, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Manejar bucket vacío (no es error, pero información útil)
            if 'message' in audit_results and audit_results['message'] == 'BUCKET_EMPTY':
                return Response(audit_results, status=status.HTTP_200_OK)
            
            return Response(audit_results, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "error": "UNEXPECTED_ERROR",
                    "message": f"Error inesperado en el servidor: {str(e)}",
                    "audit_timestamp": datetime.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

