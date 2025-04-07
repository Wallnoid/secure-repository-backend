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
    
    def get_file(self):
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

    # def firmar_documento(self, archivo_key, usuario):
    #     # Obtener el documento desde S3
    #     archivo_data = self.obtener_documento(archivo_key)
        
    #     # Firmar el documento
    #     documento_firmado = firmar_documento(archivo_data, usuario)
        
    #     # Subir documento firmado a S3 (o devolver el archivo firmado)
    #     firma_key = archivo_key.replace("documentos/", "documentos_firmados/")
    #     self.subir_documento(firma_key, documento_firmado)
        
    #     return firma_key
