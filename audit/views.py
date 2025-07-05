from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime
from django.utils import timezone

from audit.services import AuditService, LogService
from audit.serializers import (
    FileAuditRequestSerializer,
    AllFilesAuditRequestSerializer,
    FileLogSerializer,
    FolderLogSerializer,
    FileLogFilterSerializer,
    FolderLogFilterSerializer,
    FolderFilesAuditRequestSerializer,
    FileReportRequestSerializer,
    FolderReportRequestSerializer
)

audit_service = AuditService()


class FileAuditView(APIView):


    @swagger_auto_schema(
        operation_description="Get detailed audit information for a specific file using automatic bucket detection",
        tags=['Audit'],
        query_serializer=FileAuditRequestSerializer,
        responses={
            200: openapi.Response(description="File audit information retrieved successfully"),
            400: openapi.Response(description="Invalid parameters"),
            403: openapi.Response(description="Access denied to file"),
            404: openapi.Response(description="File not found"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = FileAuditRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Invalid parameters',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        file_key = data['file_key']

        try:
            audit_service = AuditService()
            result = audit_service.get_file_audit_info(file_key, username)
            
            if 'error' in result:
                if result['error'] == 'FILE_NOT_FOUND':
                    return Response(
                        {
                            'success': False,
                            'error': 'File not found',
                            'message': result.get('message', 'File does not exist in bucket'),
                            'file_key': file_key,
                            'username': username,
                            'rename_info': result.get('rename_info'),
                            'suggestion': result.get('suggestion')
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
                elif result['error'] == 'S3_ACCESS_ERROR':
                    return Response(
                        {
                            'success': False,
                            'error': 'Access denied',
                            'message': result.get('message', 'Cannot access file in S3'),
                            'file_key': file_key,
                            'username': username
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                elif result['error'] == 'BUCKET_ACCESS_ERROR':
                    return Response(
                        {
                            'success': False,
                            'error': 'Bucket not found or access denied',
                            'message': f'Cannot access bucket for user {username}. Bucket may not exist.',
                            'file_key': file_key,
                            'username': username
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
                else:
                    return Response(
                        {
                            'success': False,
                            'error': result['error'],
                            'message': result.get('message', 'Unknown error'),
                            'file_key': file_key,
                            'username': username
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            return Response(result, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error retrieving file audit: {str(e)}',
                    'file_key': file_key,
                    'username': username
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AllFilesAuditView(APIView):


    @swagger_auto_schema(
        operation_description="Get audit information for all files owned by the user using automatic bucket detection",
        tags=['Audit'],
        query_serializer=AllFilesAuditRequestSerializer,
        responses={
            200: openapi.Response(description="All files audit information retrieved successfully"),
            400: openapi.Response(description="Invalid user or authentication error"),
            404: openapi.Response(description="Bucket not found or access denied"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            audit_service = AuditService()
            result = audit_service.get_all_files_audit(username)
            
            if 'error' in result and result['error'] == 'BUCKET_ACCESS_ERROR':
                return Response(
                    {
                        'success': False,
                        'error': 'Bucket not found or access denied',
                        'message': f'Cannot access bucket for user {username}',
                        'details': result.get('message', 'Unknown error')
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'error' in result and result['error'] != 'BUCKET_EMPTY':
                return Response(
                    {
                        'success': False,
                        'error': result['error'],
                        'message': result.get('message', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            if 'error' in result and result['error'] == 'BUCKET_EMPTY':
                return Response({
                    'success': True,
                    'message': 'No files found in bucket',
                    'files_audit': [],
                    'total_files': 0,
                    'username': username,
                    'audit_timestamp': result.get('audit_timestamp', timezone.now().isoformat())
                }, status=status.HTTP_200_OK)
            
            return Response(result, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error retrieving all files audit: {str(e)}',
                    'username': username
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FolderFilesAuditView(APIView):

    @swagger_auto_schema(
        operation_description="Get audit information for all files within a specific folder using automatic bucket detection",
        tags=['Audit Reports'],
        query_serializer=FolderFilesAuditRequestSerializer,
        responses={
            200: openapi.Response(
                description="Folder files audit information retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'file_logs': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'summary': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'folder_key': openapi.Schema(type=openapi.TYPE_STRING),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'audit_timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid parameters or authentication error"),
            404: openapi.Response(description="Bucket not found or access denied"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FolderFilesAuditRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Invalid parameters',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        folder_key = data.get('key_folder', '')

        try:
            audit_service = AuditService()
            bucket_check = audit_service.get_all_files_audit(username)
            
            if 'error' in bucket_check and bucket_check['error'] == 'BUCKET_ACCESS_ERROR':
                return Response(
                    {
                        'success': False,
                        'error': 'Bucket not found or access denied',
                        'message': f'Cannot access bucket for user {username}. Bucket may not exist.',
                        'details': bucket_check.get('message', 'Unknown error')
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'error' in bucket_check and bucket_check['error'] not in ['BUCKET_EMPTY']:
                return Response(
                    {
                        'success': False,
                        'error': bucket_check['error'],
                        'message': bucket_check.get('message', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            result = AuditService.get_folder_files_logs(username, folder_key)
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve folder files audit',
                        'message': result.get('error', 'Unknown error'),
                        'username': username,
                        'folder_key': folder_key
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error retrieving folder files audit: {str(e)}',
                    'username': username,
                    'folder_key': folder_key
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileLogsView(APIView):

    @swagger_auto_schema(
        operation_description="Get file operation logs using automatic bucket detection",
        tags=['Audit'],
        query_serializer=FileLogFilterSerializer,
        responses={
            200: openapi.Response(
                description="File logs retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'total_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'applied_filters': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(description="Invalid parameters or authentication error"),
            404: openapi.Response(description="Bucket not found or access denied"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FileLogFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Invalid parameters',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        try:
            audit_service = AuditService()
            bucket_check = audit_service.get_all_files_audit(username)
            
            if 'error' in bucket_check and bucket_check['error'] == 'BUCKET_ACCESS_ERROR':
                return Response(
                    {
                        'success': False,
                        'error': 'Bucket not found or access denied',
                        'message': f'Cannot access bucket for user {username}. Bucket may not exist.',
                        'details': bucket_check.get('message', 'Unknown error')
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'error' in bucket_check and bucket_check['error'] not in ['BUCKET_EMPTY']:
                return Response(
                    {
                        'success': False,
                        'error': bucket_check['error'],
                        'message': bucket_check.get('message', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            result = AuditService.get_file_logs(
                username=username,
                file_key=data.get('file_key'),
                action=data.get('action'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                limit=data.get('limit', 100)
            )
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve file logs',
                        'message': result.get('error', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error retrieving file logs: {str(e)}',
                    'username': username
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FolderLogsView(APIView):

    @swagger_auto_schema(
        operation_description="Get folder operation logs using automatic bucket detection",
        tags=['Audit'],
        query_serializer=FolderLogFilterSerializer,
        responses={
            200: openapi.Response(
                description="Folder logs retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'total_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'applied_filters': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(description="Invalid parameters or authentication error"),
            404: openapi.Response(description="Bucket not found or access denied"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = FolderLogFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'error': 'Invalid parameters',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        try:
            audit_service = AuditService()
            bucket_check = audit_service.get_all_files_audit(username)
            
            if 'error' in bucket_check and bucket_check['error'] == 'BUCKET_ACCESS_ERROR':
                return Response(
                    {
                        'success': False,
                        'error': 'Bucket not found or access denied',
                        'message': f'Cannot access bucket for user {username}. Bucket may not exist.',
                        'details': bucket_check.get('message', 'Unknown error')
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'error' in bucket_check and bucket_check['error'] not in ['BUCKET_EMPTY']:
                return Response(
                    {
                        'success': False,
                        'error': bucket_check['error'],
                        'message': bucket_check.get('message', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            result = AuditService.get_folder_logs(
                username=username,
                folder_key=data.get('folder_key'),
                action=data.get('action'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                limit=data.get('limit', 100)
            )
            
            if result.get('success'):
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve folder logs',
                        'message': result.get('error', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error retrieving folder logs: {str(e)}',
                    'username': username
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileReportView(APIView):

    @swagger_auto_schema(
        operation_description="Generate complete file operations report using automatic bucket detection",
        tags=['Audit Reports'],
        query_serializer=FileReportRequestSerializer,
        responses={
            200: openapi.Response(
                description="File report generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'file_logs': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'statistics': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'generated_at': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid user or authentication error"),
            404: openapi.Response(description="Bucket not found or access denied"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):
        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            audit_service = AuditService()
            bucket_check = audit_service.get_all_files_audit(username)
            
            if 'error' in bucket_check and bucket_check['error'] == 'BUCKET_ACCESS_ERROR':
                return Response(
                    {
                        'success': False,
                        'error': 'Bucket not found or access denied',
                        'message': f'Cannot access bucket for user {username}',
                        'details': bucket_check.get('message', 'Unknown error')
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'error' in bucket_check and bucket_check['error'] != 'BUCKET_EMPTY':
                return Response(
                    {
                        'success': False,
                        'error': bucket_check['error'],
                        'message': bucket_check.get('message', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logs_result = AuditService.get_file_logs(
                username=username,
                limit=10000
            )
            
            if not logs_result.get('success'):
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve file logs',
                        'message': logs_result.get('error', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            stats_result = AuditService.get_user_file_stats(username)
            
            if 'error' in stats_result:
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve statistics',
                        'message': stats_result.get('error', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            response_data = {
                'success': True,
                'file_logs': logs_result.get('data', []),
                'statistics': stats_result,
                'username': username,
                'generated_at': timezone.now().isoformat(),
                'total_records': logs_result.get('total_count', 0)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error generating file report: {str(e)}',
                    'username': username
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FolderReportView(APIView):

    @swagger_auto_schema(
        operation_description="Generate complete folder operations report using automatic bucket detection",
        tags=['Audit Reports'],
        query_serializer=FolderReportRequestSerializer,
        responses={
            200: openapi.Response(
                description="Folder report generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'folder_logs': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT)
                        ),
                        'statistics': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'generated_at': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid user or authentication error"),
            404: openapi.Response(description="Bucket not found or access denied"),
            500: openapi.Response(description="Internal server error")
        }
    )
    def get(self, request):

        username = request.user.username
        
        if not username or not username.strip():
            return Response(
                {
                    'success': False,
                    'error': 'Authentication error: invalid username',
                    'message': 'User must be properly authenticated'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            audit_service = AuditService()
            bucket_check = audit_service.get_all_files_audit(username)
            
            if 'error' in bucket_check and bucket_check['error'] == 'BUCKET_ACCESS_ERROR':
                return Response(
                    {
                        'success': False,
                        'error': 'Bucket not found or access denied',
                        'message': f'Cannot access bucket for user {username}',
                        'details': bucket_check.get('message', 'Unknown error')
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if 'error' in bucket_check and bucket_check['error'] != 'BUCKET_EMPTY':
                return Response(
                    {
                        'success': False,
                        'error': bucket_check['error'],
                        'message': bucket_check.get('message', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            logs_result = AuditService.get_folder_logs(
                username=username,
                limit=10000
            )
            
            if not logs_result.get('success'):
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve folder logs',
                        'message': logs_result.get('error', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            stats_result = AuditService.get_user_folder_stats(username)
            
            if 'error' in stats_result:
                return Response(
                    {
                        'success': False,
                        'error': 'Failed to retrieve statistics',
                        'message': stats_result.get('error', 'Unknown error'),
                        'username': username
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            response_data = {
                'success': True,
                'folder_logs': logs_result.get('data', []),
                'statistics': stats_result,
                'username': username,
                'generated_at': timezone.now().isoformat(),
                'total_records': logs_result.get('total_count', 0)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'message': f'Error generating folder report: {str(e)}',
                    'username': username
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

