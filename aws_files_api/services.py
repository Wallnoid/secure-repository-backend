import boto3
from django.conf import settings



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
            raise Exception(f"Error al crear el bucket: {str(e)}")
        
    
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
            raise Exception(f"Error al subir el archivo: {str(e)}")
        

    
    def get_file(self):
        """
        This function get a file from the bucket
        @return: dict
        """
        try:
            
            
            return self.s3_client.download_file(settings.AWS_STORAGE_BUCKET_NAME, 'william-perez-english.pdf', r'C:\Users\ASUS\Downloads\william-perez-english.pdf')
   
        except Exception as e:
            raise Exception(f"Error al obtener el documento: {str(e)}")
        
    
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
            
            return response['Contents']
        except Exception as e:
            print('Error',e)
            raise Exception(f"Error al obtener los documentos: {str(e)}")
        
        

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
            raise Exception(f"Error al subir el archivo: {str(e)}")


    def get_principal_folders(self,bucket_name):
        """
        This function get the principal folders of the bucket
        @param bucket_name: str
        @return: list
        """
        try:
            response = self.s3_client.list_objects(Bucket=bucket_name)
            
            folders = [obj for obj in response['Contents'] if obj['Key'].endswith('/') and obj['Key'].count('/') == 1]
            
             
            return folders
        except Exception as e:
            raise Exception(f"Error al obtener las carpetas: {str(e)}")
        
        
    def get_files_by_folder_key(self,bucket_name,folder_key):
        """
        This function get the folders of a folder
        @param bucket_name: str
        @param folder_key: str
        @return: list
        """
        
        #TODO: PENSAR EN UNA FORMA DE QUE NO SE OBTENGAN TODAS LAS CARPETAS, SOLO LAS QUE ESTAN DENTRO DE LA CARPETA con el folderKey refiriendome a que solo aparezcan los folderKey/carpeta y que no se muestren las carpetaso archivos como folderKey/folert3/archivo.pdf
        try:
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            files = [obj for obj in response['Contents'] if obj['Key'].count('/') == 1]
            
            return files
        except Exception as e:
            raise Exception(f"Error al obtener las carpetas: {str(e)}")
