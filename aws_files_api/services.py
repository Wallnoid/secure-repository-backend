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
        
 
 
# Bucket functions
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
        
 
    # File functions
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
        

    def get_file(self, bucket_name, file_name):
        """
        This function get a file from the bucket
        @param bucket_name: str
        @param file_name: str
        @return: bytes - contenido del archivo
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=file_name)
            return response['Body'].read()
   
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
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            
            prefix_length = len(folder_key)
            
            filtered_items = []
            seen_items = set()  
            
            files = response.get('Contents', [])
            
           
            for obj in files:
               
                key = obj['Key']
                
                print(key)
                
                if key == f"{folder_key}":
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
        
        
    def update_file_name(self,bucket_name,file_key,new_file_key):
        """
        This function update the name of a file in the bucket
        @param bucket_name: str
        @param file_key: str
        @param new_file_key: str
        """
        try:
            response = self.s3_client.copy_object(Bucket=bucket_name, CopySource=f'{bucket_name}/{file_key}', Key=new_file_key)
            
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                self.s3_client.delete_object(Bucket=bucket_name, Key=file_key)
                return response
            else:
                raise Exception(f"Error: {response['ResponseMetadata']['HTTPStatusCode']}")
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        
        
    def delete_file(self,bucket_name,file_key):
        """
        This function delete a file from the bucket
        @param bucket_name: str
        @param file_key: str
        """
        try:
            return self.s3_client.delete_object(Bucket=bucket_name, Key=file_key)
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
        
        

# Folder functions

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
        
        
    def update_folder_name(self,bucket_name, folder_key, new_folder_key):
        """
        Safely rename a 'folder' in an S3 bucket by copying and then deleting.
        @param bucket_name: str
        @param folder_key: str
        @param new_folder_key: str
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            all_objects = []

            for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_key):
                all_objects.extend(page.get('Contents', []))

            if not all_objects:
                raise Exception(f"No se encontraron objetos bajo {folder_key}")

            for obj in all_objects:
                if obj['Key'].endswith('/'):
                    continue  

                old_key = obj['Key']
                new_key = old_key.replace(folder_key, new_folder_key, 1)

                self.s3_client.copy_object(
                    Bucket=bucket_name,
                    CopySource={'Bucket': bucket_name, 'Key': old_key},
                    Key=new_key
                )

            for obj in all_objects:
                if obj['Key'].endswith('/'):
                    continue
                self.s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                                
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{new_folder_key}")

            self.s3_client.delete_object(Bucket=bucket_name, Key=folder_key)

            return True

        except Exception as e:
            raise Exception(f"Error al renombrar la carpeta: {str(e)}")

        
        
    def delete_folder(self,bucket_name,folder_key):
        """
        This function delete a folder from the bucket
        @param bucket_name: str
        @param folder_key: str
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            response = paginator.paginate(Bucket=bucket_name, Prefix=folder_key)
            for page in response:
                for obj in page.get('Contents', []):
                    self.s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
            return True
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
