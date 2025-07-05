from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import HttpResponse

from aws_files_api.serializers import UploadFileSerializer, UpdateFileSerializer, DeleteFileSerializer, DownloadFileSerializer, GetFilesByFolderSerializer, ResponseFileSerializer
from shared_files.serializers import SharedFileSerializer, DeleteSharedFileSerializer, GetSharedFilesSerializer
from aws_files_api.serializers import CreateBucketSerializer, CreateFolderSerializer, UpdateFolderNameSerializer, DeleteFolderSerializer
from aws_files_api.services import AWSFileService
from shared_files.services import SharedFileService
from audit.services import LogService

file_service = AWSFileService()
shared_file_service = SharedFileService()

class CreateBucket(APIView):    
    def get(self, request):
        try:
            file_service.create_bucket(request.user.username)
            return Response({"message": "Bucket created successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class FilesView(APIView):
    parser_classes = [  MultiPartParser, FormParser]
    
    @swagger_auto_schema(query_serializer=GetFilesByFolderSerializer)
    def get(self, request):
        try:
            
            serializer = GetFilesByFolderSerializer(data=request.query_params)
            if serializer.is_valid():
                folder_key = serializer.validated_data['folder_key']
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            folder_key = f"{folder_key}/" if folder_key else ""

            documentos = file_service.get_files_by_folder_key(f'{request.user.username}-security-project', f'{folder_key}')
            return Response(documentos, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
             
    @swagger_auto_schema(
        request_body=UploadFileSerializer,
        consumes=["multipart/form-data"])
    def post(self, request):
        serializer = UploadFileSerializer(data=request.data)
        if serializer.is_valid():
            file_name = serializer.validated_data['file_name']
            file = serializer.validated_data['file']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bucket_name = f"{request.user.username}-security-project"
        
        try:
            result = file_service.upload_file(
                bucket_name=bucket_name,
                file_name=file_name,
                data=file
            )
            
            if result['status'] == 'error':
                LogService.log_file_action(
                    user_id=request.user.username,
                    user_email=getattr(request.user, 'email', ''),
                    action='UPLOAD',
                    file_key=file_name,
                    file_name=file_name.split('/')[-1],
                    bucket_name=bucket_name,
                    request=request,
                    file_size=file.size,
                    success=False,
                    error_message=result['message']
                )
                
                return Response({
                    "error": result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='UPLOAD',
                file_key=file_name,
                file_name=file_name.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                file_size=result.get('original_size', file.size),
                success=True
            )
            
            response_data = {
                "message": result['message'],
                "file_type": result['file_type']
            }
            
            if result['file_type'] == 'binary_encrypted_as_pdf':
                response_data.update({
                    "original_size": result.get('original_size'),
                    "encrypted_size": result.get('encrypted_size'),
                    "encryption_algorithm": result.get('encryption_algorithm')
                })
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='UPLOAD',
                file_key=file_name,
                file_name=file_name.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                file_size=file.size,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(request_body=UpdateFileSerializer)
    def put(self, request):
        serializer = UpdateFileSerializer(data=request.data)
        if serializer.is_valid():
            file_key = serializer.validated_data['file_key']
            new_file_key = serializer.validated_data['new_file_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bucket_name = f"{request.user.username}-security-project"
        
        try:
            response = file_service.update_file_name(bucket_name, file_key, new_file_key)
            shared_file_service.update_file_key(file_key, new_file_key)
            
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='UPDATE',
                file_key=new_file_key,
                file_name=new_file_key.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                old_file_name=file_key.split('/')[-1],
                success=True
            )
            
            return Response({
                "message": "File updated successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='UPDATE',
                file_key=file_key,
                file_name=file_key.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @swagger_auto_schema(query_serializer=DeleteFileSerializer)
    def delete(self, request):
        serializer = DeleteFileSerializer(data=request.query_params)
        if serializer.is_valid():
            file_key = serializer.validated_data['file_key']
        else:            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bucket_name = f"{request.user.username}-security-project"
        
        try:
            response = file_service.delete_file(bucket_name, file_key)
            shared_file_service.delete_by_file_key(file_key)
            
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='DELETE',
                file_key=file_key,
                file_name=file_key.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                success=True
            )
            
            return Response({
                "message": "File deleted successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='DELETE',
                file_key=file_key,
                file_name=file_key.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class DownloadFile(APIView):
    
    @swagger_auto_schema(query_serializer=DownloadFileSerializer)
    def get(self, request):
        serializer = DownloadFileSerializer(data=request.query_params)
        if serializer.is_valid():
            file_key = serializer.validated_data['file_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        owner_user_id = serializer.validated_data.get('owner_user_id')
        if owner_user_id:
            bucket_name = f"{owner_user_id}-security-project"
            is_shared_file = True
        else:
            bucket_name = f"{request.user.username}-security-project"
            is_shared_file = False
            owner_user_id = request.user.username
        
        try:
            if is_shared_file:
                print(f"Downloading file from bucket: {bucket_name} its shared")
                result = file_service.get_file(bucket_name=bucket_name, file_name=file_key)
            else:
                print(f"Downloading file from bucket: {bucket_name} its the owner")
                result = file_service.get_file(bucket_name=bucket_name, file_name=file_key)
            
            if result['status'] == 'error':
                LogService.log_file_action(
                    user_id=request.user.username,
                    user_email=getattr(request.user, 'email', ''),
                    action='DOWNLOAD',
                    file_key=file_key,
                    file_name=file_key.split('/')[-1],
                    bucket_name=bucket_name,
                    request=request,
                    owner_user_id=owner_user_id if is_shared_file else None,
                    success=False,
                    error_message=result['message']
                )
                
                return Response({
                    "error": result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            file_content = result['file_content']
            file_name = file_key.split('/')[-1]
            
            if result['file_type'] == 'binary_decrypted_from_pdf':
                content_type = 'application/octet-stream'
                # Cambiar extensión de .pdf a .bin para descarga
                if file_name.endswith('.pdf'):
                    file_name = file_name.replace('.pdf', '.bin')
            elif result['file_type'] == 'binary_encrypted_as_pdf':
                content_type = 'application/octet-stream'
                # Cambiar extensión de .pdf a .bin para descarga
                if file_name.endswith('.pdf'):
                    file_name = file_name.replace('.pdf', '.bin')
            else:
                content_type = 'application/octet-stream'
            
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='DOWNLOAD',
                file_key=file_key,
                file_name=file_key.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                file_size=len(file_content) if file_content else None,
                owner_user_id=owner_user_id if is_shared_file else None,
                success=True
            )
            
            response = HttpResponse(
                file_content,
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            
            # Agregar headers informativos para archivos .bin cifrados
            if result['file_type'] in ['binary_decrypted_from_pdf', 'binary_encrypted_as_pdf']:
                response['X-File-Type'] = result['file_type']
                if result.get('decryption_algorithm'):
                    response['X-Decryption-Algorithm'] = result['decryption_algorithm']
                if result.get('message'):
                    response['X-Processing-Message'] = result['message']
            
            return response
            
        except Exception as e:
            LogService.log_file_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='DOWNLOAD',
                file_key=file_key,
                file_name=file_key.split('/')[-1],
                bucket_name=bucket_name,
                request=request,
                owner_user_id=owner_user_id if is_shared_file else None,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class PrincipalFolder(APIView):
    parser_classes = [ JSONParser]
    
    def get(self, request):
        try:
            response = file_service.get_principal_folders(f'{request.user.username}-security-project')
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
               
                
class FolderCrud(APIView):
    
    @swagger_auto_schema(request_body=CreateFolderSerializer)
    def post(self, request):
        serializer = CreateFolderSerializer(data=request.data)
        if serializer.is_valid():
            folder_key = serializer.validated_data['folder_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bucket_name = f'{request.user.username}-security-project'
        
        try:
            response = file_service.create_folder(bucket_name, folder_key)
            
            LogService.log_folder_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='CREATE',
                folder_key=f'{folder_key}/',
                folder_name=folder_key.split('/')[-1] if '/' in folder_key else folder_key,
                bucket_name=bucket_name,
                request=request,
                parent_folder='/'.join(folder_key.split('/')[:-1]) if '/' in folder_key else '',
                success=True
            )
            
            return Response({
                "message": "Folder created successfully",
                "folder_key": folder_key,
                "response": response
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            LogService.log_folder_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='CREATE',
                folder_key=f'{folder_key}/',
                folder_name=folder_key.split('/')[-1] if '/' in folder_key else folder_key,
                bucket_name=bucket_name,
                request=request,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @swagger_auto_schema(request_body=UpdateFolderNameSerializer)
    def put(self, request):
        serializer = UpdateFolderNameSerializer(data=request.data)
        if serializer.is_valid():
            folder_key = serializer.validated_data['folder_key']
            new_folder_key = serializer.validated_data['new_folder_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bucket_name = f'{request.user.username}-security-project'
        
        try:
            response = file_service.update_folder_name(bucket_name, f'{folder_key}/', f'{new_folder_key}/')
            shared_file_service.update_folder_key(folder_key, new_folder_key)
            
            LogService.log_folder_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='UPDATE',
                folder_key=f'{new_folder_key}/',
                folder_name=new_folder_key.split('/')[-1] if '/' in new_folder_key else new_folder_key,
                bucket_name=bucket_name,
                request=request,
                old_folder_name=folder_key.split('/')[-1] if '/' in folder_key else folder_key,
                parent_folder='/'.join(new_folder_key.split('/')[:-1]) if '/' in new_folder_key else '',
                success=True
            )
            
            return Response({
                "message": "Folder updated successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            LogService.log_folder_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='UPDATE',
                folder_key=f'{folder_key}/',
                folder_name=folder_key.split('/')[-1] if '/' in folder_key else folder_key,
                bucket_name=bucket_name,
                request=request,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @swagger_auto_schema(query_serializer=DeleteFolderSerializer)
    def delete(self, request):
        serializer = DeleteFolderSerializer(data=request.query_params)
        if serializer.is_valid():
            folder_key = serializer.validated_data['folder_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        bucket_name = f'{request.user.username}-security-project'
        
        try:
            response = file_service.delete_folder(bucket_name, f'{folder_key}/')
            shared_file_service.delete_folder(folder_key)
            
            LogService.log_folder_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='DELETE',
                folder_key=f'{folder_key}/',
                folder_name=folder_key.split('/')[-1] if '/' in folder_key else folder_key,
                bucket_name=bucket_name,
                request=request,
                parent_folder='/'.join(folder_key.split('/')[:-1]) if '/' in folder_key else '',
                success=True
            )
            
            return Response({
                "message": "Folder deleted successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            LogService.log_folder_action(
                user_id=request.user.username,
                user_email=getattr(request.user, 'email', ''),
                action='DELETE',
                folder_key=f'{folder_key}/',
                folder_name=folder_key.split('/')[-1] if '/' in folder_key else folder_key,
                bucket_name=bucket_name,
                request=request,
                success=False,
                error_message=str(e)
            )
            
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
