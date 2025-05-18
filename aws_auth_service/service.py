import boto3
from django.conf import settings



class AWSCognitoService:
    def __init__(self):
        self.cognito_client = boto3.client(
            'cognito-idp',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            
        )
    
    def get_user(self):
        try:
            
            print('descargando archivo')
            # Descargar archivo de S3
            self.s3_client.download_file(settings.AWS_STORAGE_BUCKET_NAME, 'william-perez-english.pdf', r'C:\Users\ASUS\Downloads\william-perez-english.pdf')
            print('archivo descargado')
            
            
            
            return {"message": "Archivo descargado con éxito", "archivo": "william-perez-english.pdf"}
        except Exception as e:
            raise Exception(f"Error al obtener el documento: {str(e)}")
        
    
    def get_all_files(self):
        try:  
            response = self.s3_client.list_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME
                
                
            )
            
            print(response)
            return response['Contents']
        except Exception as e:
            print('Error',e)
            raise Exception(f"Error al obtener los documentos: {str(e)}")
        
        

    # def subir_documento(self, archivo_key, archivo_data):
    #     try:
    #         # Subir archivo a S3
    #         self.s3_client.upload_fileobj(archivo_data, settings.AWS_STORAGE_BUCKET_NAME, archivo_key)
    #     except Exception as e:
    #         raise Exception(f"Error al subir el archivo: {str(e)}")
