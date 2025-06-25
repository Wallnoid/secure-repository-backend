import boto3
from django.conf import settings
import re
import io
from datetime import datetime

from aws_files_api.serializers import ResponseFileSerializer
from files_encryption.encryption_service import FileEncryptionService
from files_decryption.decryption_service import FileDecryptionService


class AWSFileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            
        )
        
        # Inicializar servicios de cifrado/descifrado
        self.encryption_service = FileEncryptionService()
        self.decryption_service = FileDecryptionService()


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
        
 
    def upload_file(self, bucket_name, file_name, data, metadata=None):
        """
        This function upload a file to the bucket with automatic encryption
        @param bucket_name: str
        @param file_name: str
        @param data: file object or str
        @param metadata: dict - optional metadata
        @return: dict with upload result
        """
        try:
            
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=file_name)
            if 'Contents' in response and any(obj['Key'] == file_name+'.pdf' for obj in response['Contents']):
                print(f"File '{file_name}' already exists ")
                raise Exception(f"File '{file_name}' already exists ")
                
            # Obtener el nombre real del archivo desde el objeto data
            actual_file_name = getattr(data, 'name', file_name) if hasattr(data, 'name') else file_name
            
            # Detectar si es archivo .bin para cifrado
            if actual_file_name.lower().endswith('.bin'):

                try:
                    if hasattr(data, 'read'):
                        binary_content = data.read()
                        original_size = len(binary_content)
                    else:
                        binary_content = data
                        original_size = len(binary_content)
                    
                    # Cifrar contenido
                    encrypted_bytes = self.encryption_service.encrypt_binary_content(binary_content)
                    encrypted_size = len(encrypted_bytes)
                    
                    encrypted_stream = io.BytesIO(encrypted_bytes)
                    s3_response = self.s3_client.upload_fileobj(encrypted_stream, bucket_name, file_name+'.pdf')
                    
                    
                    return {
                        'status': 'success',
                        'message': 'file .bin uploaded and encrypted successfully',
                        'file_type': 'binary_encrypted_as_pdf',
                        'original_size': original_size,
                        'encrypted_size': encrypted_size,
                        'encryption_algorithm': 'AES-128-Binary-Custom',
                        'storage_method': 'memory_only',
                        'display_extension': '.pdf',
                        'actual_type': '.bin',
                        's3_response': s3_response
                    }
                    
                except Exception as encrypt_error:
                    return {
                        'status': 'error',
                        'message': f"Error during encryption: {str(encrypt_error)}",
                        'file_type': 'binary_encrypted'
                    }
            else:
                # Solo se aceptan archivos .bin
                return {
                    'status': 'error',
                    'message': 'Only .bin files are allowed for upload',
                    'file_type': 'unsupported'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error: {str(e)}",
                'file_type': 'unknown'
            }
        

    def get_file(self, bucket_name, file_name, decrypt_if_binary=True):
        """
        This function get a file from the bucket with automatic decryption for encrypted 
        @param bucket_name: str
        @param file_name: str
        @param decrypt_if_binary: bool - whether to decrypt files automatically
        @return: dict with file data and metadata
        """
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=file_name)
            file_content = response['Body'].read()
            
            if file_name.lower().endswith('.pdf') and decrypt_if_binary:
                # Descifrar en memoria 
                try:
                    start_time = datetime.now()
                    
                    # Descifrar contenido directamente en memoria
                    decrypted_content = self.decryption_service.decrypt_binary_content(file_content)
                    
                    end_time = datetime.now()
                    decryption_time = (end_time - start_time).total_seconds()
                    
                    return {
                        'status': 'success',
                        'file_content': decrypted_content,
                        'file_type': 'binary_decrypted_from_pdf',
                        'original_size': len(decrypted_content),
                        'encrypted_size': len(file_content),
                        'decryption_algorithm': 'AES-128-Binary-Custom',
                        'decryption_time': f"{decryption_time:.3f}s",
                        'processing_method': 'memory_only',
                        'display_extension': '.pdf',
                        'actual_type': '.bin'
                    }
                    
                except Exception as decrypt_error:
                    # Si falla el descifrado, devolver archivo sin descifrar
                    return {
                        'status': 'warning',
                        'file_content': file_content,
                        'file_type': 'binary_encrypted_as_pdf',
                        'message': f"Error during decryption: {str(decrypt_error)}",
                        'display_extension': '.pdf',
                        'actual_type': '.bin'
                    }
            else:
                # Devolver archivo sin descifrar si se solicita
                return {
                    'status': 'success',
                    'file_content': file_content,
                    'file_type': 'encrypted_binary_as_pdf',
                    'display_extension': '.pdf',
                    'actual_type': '.bin'
                }
   
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error: {str(e)}",
                'file_type': 'unknown'
            }
        
        
    def get_files_by_folder_key(self, bucket_name, folder_key):
        """
        This function get the files and folders directly inside the specified folder_key
        @param bucket_name: str
        @param folder_key: str
        @return: list of files and folders in the first level only
        """
        try:
            
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)
            if 'Contents' in response and any(obj['Key'] == folder_key+"/" for obj in response['Contents']):
                print(f"Folder '{folder_key}' already exists ")
                raise Exception(f"Folder '{folder_key}' already exists ")
                
            
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
                    
                    obj_with_type = obj.copy()
                    if key.endswith('.pdf'):
                        obj_with_type['file_type'] = 'binary_encrypted_as_pdf'
                        obj_with_type['display_extension'] = '.pdf'
                        obj_with_type['actual_type'] = '.bin'
                        obj_with_type['encrypted'] = True
                    else:
                        obj_with_type['file_type'] = 'folder'
                    
                    filtered_items.append(obj_with_type)
            
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
            
            # Validar si el archivo ya existe
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=new_file_key)
            if 'Contents' in response and any(obj['Key'] == new_file_key+'.pdf' for obj in response['Contents']):
                print(f"File '{new_file_key}.pdf' already exists in bucket ")
                raise Exception(f"File '{new_file_key}.pdf' already exists in bucket ")
            
            # Validar si el archivo original existe
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=file_key)
            if 'Contents' not in response or not any(obj['Key'] == file_key for obj in response['Contents']):
                print(f"File '{file_key}' does not exist in bucket ")
                raise Exception(f"File '{file_key}' does not exist in bucket ")
            
            
            response = self.s3_client.copy_object(Bucket=bucket_name, CopySource=f'{bucket_name}/{file_key}', Key=new_file_key+'.pdf')
            
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
            
            # Validar si el archivo existe
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=file_key)
            if 'Contents' not in response or not any(obj['Key'] == file_key for obj in response['Contents']):
                print(f"File '{file_key}' does not exist in bucket ")
                raise Exception(f"File '{file_key}' does not exist in bucket ")
                                                     
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
            
            files_with_metadata = []
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.pdf'):
                    obj_with_metadata = obj.copy()
                    obj_with_metadata['file_type'] = 'binary_encrypted_as_pdf'
                    obj_with_metadata['display_extension'] = '.pdf'
                    obj_with_metadata['actual_type'] = '.bin'
                    obj_with_metadata['encrypted'] = True
                    files_with_metadata.append(obj_with_metadata)
                elif obj['Key'].endswith('/'):
                    # Incluir carpetas
                    obj_with_metadata = obj.copy()
                    obj_with_metadata['file_type'] = 'folder'
                    files_with_metadata.append(obj_with_metadata)
            
            serializer = ResponseFileSerializer(files_with_metadata, many=True)
            
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
            
            # VALIDATE IF FOLDER KEY NON EXIST ON BUCKET
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            
            if 'Contents' in response and any(obj['Key'] == folder_key+'/' for obj in response['Contents']):
                print(f"Folder '{folder_key}' already exists in bucket ")
                raise Exception(f"Folder '{folder_key}' already exists in bucket ")
            
            
            
            print(response) 
           
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
            
            # Validar si la carpeta ya existe
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=new_folder_key)
            if 'Contents' in response and any(obj['Key'] == new_folder_key for obj in response['Contents']):
                print(f"Folder '{new_folder_key}' already exists in bucket ")
                raise Exception(f"Folder '{new_folder_key}' already exists in bucket ")
            
            # Validar si la carpeta original existe
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            if 'Contents' not in response or not any(obj['Key'] == folder_key for obj in response['Contents']):
                print(f"Folder '{folder_key}' does not exist in bucket ")
                raise Exception(f"Folder '{folder_key}' does not exist in bucket ")
            
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            all_objects = []

            for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_key):
                all_objects.extend(page.get('Contents', []))

            if not all_objects:
                raise Exception(f"No se encontraron objetos bajo {folder_key}")

            for obj in all_objects:
                old_key = obj['Key']
                new_key = old_key.replace(folder_key, new_folder_key, 1)

                copy_source = {'Bucket': bucket_name, 'Key': old_key}
                self.s3_client.copy_object(
                    CopySource=copy_source,
                    Bucket=bucket_name,
                    Key=new_key
                )

            for obj in all_objects:
                self.s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])

            return {
                "status": "success",
                "message": f"Carpeta renombrada de '{folder_key}' a '{new_folder_key}' exitosamente."
            }
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
        
        
    def delete_folder(self,bucket_name,folder_key):
        """
        This function delete a folder from the bucket
        @param bucket_name: str
        @param folder_key: str
        """
        try:
            
            # Validar si la carpeta existe
            validate_response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            if 'Contents' not in validate_response or not any(obj['Key'] == folder_key for obj in validate_response['Contents']):
                print(f"Folder '{folder_key}' does not exist in bucket ")
                raise Exception(f"Folder '{folder_key}' does not exist in bucket ")
            
            
            
            
            response = self.s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    self.s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
            
            return response
        except Exception as e:
            raise Exception(f"Error: {str(e)}")
