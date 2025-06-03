from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aws_files_api.serializers import CreateFolderSerializer, DeleteFileSerializer, DownloadFileSerializer, FolderGetSerializer, GetFilesByFolderSerializer, UpdateFileSerializer, UploadFileSerializer, UpdateFolderNameSerializer, DeleteFolderSerializer
from aws_files_api.services import AWSFileService
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from shared_files.services import SharedFileService
from django.http import HttpResponse

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
        
        try:
            response = file_service.upload_file(f"{request.user.username}-security-project",file_name,file)
            
            return Response({
                "message": "File uploaded successfully",
               
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(request_body=UpdateFileSerializer)
    def put(self, request):
        serializer = UpdateFileSerializer(data=request.data)
        if serializer.is_valid():
            file_key = serializer.validated_data['file_key']
            new_file_key = serializer.validated_data['new_file_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = file_service.update_file_name(f"{request.user.username}-security-project",file_key,new_file_key)
            shared_file_service.update_file_key(file_key, new_file_key)
            return Response({
                "message": "File updated successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @swagger_auto_schema(query_serializer=DeleteFileSerializer)
    def delete(self, request):
        serializer = DeleteFileSerializer(data=request.query_params)
        if serializer.is_valid():
            file_key = serializer.validated_data['file_key']
        else:            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = file_service.delete_file(f"{request.user.username}-security-project",file_key)
            shared_file_service.delete(file_key)
            
            return Response({
                "message": "File deleted successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class DownloadFile(APIView):
    
    @swagger_auto_schema(query_serializer=DownloadFileSerializer)
    def get(self, request):
        serializer = DownloadFileSerializer(data=request.query_params)
        if serializer.is_valid():
            file_key = serializer.validated_data['file_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_content = file_service.get_file(f"{request.user.username}-security-project", file_key)
            file_name = file_key.split('/')[-1]
            
            response = HttpResponse(
                file_content,
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
            
        except Exception as e:
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
        
        try:
            response = file_service.create_folder(f'{request.user.username}-security-project',folder_key)
            return Response({
                "message": "Folder created successfully",
                "folder_key": folder_key,
                "response": response
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @swagger_auto_schema(request_body=UpdateFolderNameSerializer)
    def put(self, request):
        serializer = UpdateFolderNameSerializer(data=request.data)
        if serializer.is_valid():
            folder_key = serializer.validated_data['folder_key']
            new_folder_key = serializer.validated_data['new_folder_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = file_service.update_folder_name(f'{request.user.username}-security-project',f'{folder_key}/',f'{new_folder_key}/')
            
            shared_file_service.update_folder_key(folder_key, new_folder_key)
            return Response({
                "message": "Folder updated successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    @swagger_auto_schema(query_serializer=DeleteFolderSerializer)
    def delete(self, request):
        serializer = DeleteFolderSerializer(data=request.query_params)
        if serializer.is_valid():
            folder_key = serializer.validated_data['folder_key']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = file_service.delete_folder(f'{request.user.username}-security-project',f'{folder_key}/')
            shared_file_service.delete_folder(folder_key)
            return Response({
                "message": "Folder deleted successfully",
                "response": response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
