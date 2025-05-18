from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aws_files_api.serializers import CreateFolderSerializer, UploadFileSerializer
from aws_files_api.services import AWSFileService
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser



file_service = AWSFileService()


class CreateBucket(APIView):    
    def get(self, request):
        try:
            file_service.create_bucket(request.user.username)
            return Response({"message": "Bucket created successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class GetFilesView(APIView):
    def get(self, request):
        try:
            documentos = file_service.get_all_files(request.user.username)
            return Response(documentos, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class DownloadFile(APIView):
    def get(self, request):
        try:
            documento = file_service.get_file()
            return Response(documento, content_type='application/octet-stream', status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

class UploadFile(APIView):
    parser_classes = [  MultiPartParser, FormParser]
     
    @swagger_auto_schema(
        request_body=UploadFileSerializer,
        consumes=["multipart/form-data"]
                         )
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
               
                
class FolderCrud(APIView):
    parser_classes = [ JSONParser]
    
    def get(self, request):
        
        try:
            print(request)
            response = file_service.get_principal_folders(f'{request.user.username}-security-project')
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
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
