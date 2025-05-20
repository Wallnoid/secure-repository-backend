import boto3
from django.conf import settings
import re

from aws_files_api.serializers import ResponseFileSerializer



class AWSFileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            
        )
        
        
    def create_bucket(self, bucket_name):
        """
        This function create a bucket in the s3
        @param bucket_name: str
        @return: dict
        """
        try:
            return self.s3_client.create_bucket(Bucket=f'{bucket_name}-security-project')
            
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        
    
    def upload_file(self,bucket_name,file_name,data):
        """
        This function upload a file to the bucket
        @param bucket_name: str
        @param file_name: str
        @param data: str
        """
        try:
            return self.s3_client.upload_fileobj(data,bucket_name,file_name)
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        

    
    def get_file(self):
        """
        This function get a file from the bucket
        @return: dict
        """
        try:
            
            
            
            
            return self.s3_client.download_file(settings.AWS_STORAGE_BUCKET_NAME, 'william-perez-english.pdf', r'C:\Users\ASUS\Downloads\william-perez-english.pdf')
   
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        
    
    def get_all_files(self,bucket_name):
        """
        This function get all the files in the bucket
        @param bucket_name: str
        @return: list
        """
        try:  
            response = self.s3_client.list_objects(
                Bucket=f"{bucket_name}-security-project"
                
                
            )
            
            serializer = ResponseFileSerializer(response['Contents'], many=True)
            
            return serializer.data
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        
        

    def create_folder(self, bucket_name,folder_key):
        """
        This function create a folder in the bucket
        @param bucket_name: str
        @param folder_key: str
        @return: dict
        """
        try:
           
            return self.s3_client.put_object(Bucket=bucket_name, Key=f'{folder_key}/')
        except Exception as e:
            raise Exception(f"Error: {str(e)}")


    def get_principal_folders(self,bucket_name):
        """
        This function get the principal folders of the bucket
        @param bucket_name: str
        @return: list
        """
        try:
            response = self.s3_client.list_objects(Bucket=bucket_name)
            
            folders = [obj for obj in response['Contents'] if obj['Key'].endswith('/') and obj['Key'].count('/') == 1]
            
            serializer = ResponseFileSerializer(folders, many=True)
            
            return serializer.data
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        
        
    def get_files_by_folder_key(self,bucket_name,folder_key):
        """
        This function get the files and folders directly inside the specified folder_key
        @param bucket_name: str
        @param folder_key: str
        @return: list of files and folders in the first level only
        """
        try:
            print(folder_key)
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            
            prefix_length = len(folder_key)
            
            filtered_items = []
            seen_items = set()  
            
            
            files = response.get('Contents', [])
            
            
            for obj in files:
               
                key = obj['Key']
                
                if key == f"{folder_key}/":
                    continue
                
                remaining_path = key[prefix_length:].lstrip('/')
                
                if re.search(r'/.', remaining_path):
                    continue
                
                if not key.endswith('/'):
                    if not key.endswith('.pdf'):
                        continue
                
                if remaining_path not in seen_items:
                    seen_items.add(remaining_path)
                    filtered_items.append(obj)
            
            serializer = ResponseFileSerializer(filtered_items, many=True)
            
            return serializer.data
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
