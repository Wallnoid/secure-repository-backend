

from shared_files.serializers import DeleteSharedFileSerializer, GetSharedFilesByFileKeySerializer, GetSharedFilesSerializer, SharedFileSerializer
from shared_files.services import SharedFileService
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser



shared_file_service = SharedFileService()



class SharedFileView(APIView):
    parser_classes = [ JSONParser]
   
    def get(self, request):
        try:
            username = request.user.username
            if username == "":
                return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            shared_files = shared_file_service.get_by_shared_with_user_id(username)
            print(shared_files)
            return Response({"message": "Shared files retrieved successfully", "shared_files": shared_files.values()}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @swagger_auto_schema(request_body=SharedFileSerializer)
    def post(self, request):
        try:
            username = request.user.username
            
            if username == "":
                return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
            serializer = SharedFileSerializer(data=request.data)
            
            if serializer.is_valid():
                
                user_to_share = []
                skipped_users = []
                
                for user in serializer.validated_data["shared_with_users"]:
                    
                    if shared_file_service.is_the_same_shared_file(
                        serializer.validated_data["file_key"],
                        username,
                        user["id"]
                    ):
                        skipped_users.append(user["email"])
                    else:
                        user_to_share.append(user)
                        
                
                if not user_to_share:
                    return Response({"message": "No new users to share with. Skipped users: " + ", ".join(skipped_users)}, status=status.HTTP_400_BAD_REQUEST)
                
                
                    
                for user in user_to_share:
                    

                    shared_file_service.save({
                        "owner_user_id": username,
                        "owner_user_email": request.user.email,
                        "bucket_name": username,    
                        "file_key": serializer.validated_data["file_key"],
                        "file_name": serializer.validated_data["file_name"],
                        "file_size": serializer.validated_data["file_size"],
                        "shared_with_user_email": user["email"],
                        "shared_with_user_id": user["id"]
                })
                return Response({"message": "Shared file created successfully",
                                 "shared_with_users": user_to_share,
                                 "skipped_users": skipped_users}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

        
    @swagger_auto_schema(query_serializer=DeleteSharedFileSerializer)
    def delete(self, request):
        try:
            username = request.user.username    
            if username == "":
                return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = DeleteSharedFileSerializer(data=request.query_params)
            if serializer.is_valid():   
                shared_file_service.delete(serializer.validated_data["id"])
                return Response({"message": "Shared file deleted successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)  
        
    
    
    
class SharedFileByFileKey(APIView):
    
    @swagger_auto_schema(query_serializer=GetSharedFilesByFileKeySerializer)
    def get(self, request):
        try:
            username = request.user.username
            if username == "":
                return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = GetSharedFilesByFileKeySerializer(data=request.query_params)
            if serializer.is_valid():
                shared_files = shared_file_service.get_by_file_key(serializer.validated_data["file_key"], username)
                
                shared_files = [{"id": file.id, "shared_with_user_id": file.shared_with_user_id, "shared_with_user_email": file.shared_with_user_email, "shared_at": file.shared_at} for file in shared_files]
                return Response({"message": "Shared files retrieved successfully", "shared_files": shared_files}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    


