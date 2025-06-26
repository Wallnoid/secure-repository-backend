import boto3
from django.conf import settings
from shared_files.models import SharedFile
from datetime import datetime


class AuditService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

    def get_file_audit_info(self, file_key, user_id=None, user_email=None):
        try:
            if user_id:
                bucket_name = f"{user_id}-security-project"
            else:
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # Primero verificar si el archivo existe en S3
            file_exists = self._check_file_exists(bucket_name, file_key)
            if not file_exists:
                return {
                    'error': 'FILE_NOT_FOUND',
                    'message': f'El archivo "{file_key}" no existe en el bucket',
                    'file_key': file_key,
                    'audit_timestamp': datetime.now().isoformat()
                }

            s3_metadata = self._get_s3_file_metadata(bucket_name, file_key)
            
            # Si hay error en metadatos de S3, devolver error completo
            if 's3_error' in s3_metadata:
                return {
                    'error': 'S3_ACCESS_ERROR',
                    'message': f'Error accediendo al archivo en S3: {s3_metadata["s3_error"]}',
                    'file_key': file_key,
                    'audit_timestamp': datetime.now().isoformat()
                }
            
            shared_info = self._get_shared_file_info(file_key)
            owner_info = self._get_owner_info(file_key, user_id, user_email)
            
            audit_info = {
                'file_key': file_key,
                's3_metadata': s3_metadata,
                'shared_info': shared_info,
                'owner_info': owner_info,
                'audit_timestamp': datetime.now().isoformat()
            }
            
            return audit_info
            
        except Exception as e:
            return {
                'error': 'GENERAL_ERROR',
                'message': f'Error inesperado obteniendo información de auditoría: {str(e)}',
                'file_key': file_key,
                'audit_timestamp': datetime.now().isoformat()
            }

    def _check_file_exists(self, bucket_name, file_key):
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=file_key)
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except Exception:
            return False

    def _get_s3_file_metadata(self, bucket_name, file_key):
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=file_key)
            
            object_info = {}
            try:
                object_info = self.s3_client.get_object_attributes(
                    Bucket=bucket_name,
                    Key=file_key,
                    ObjectAttributes=['ObjectSize', 'ETag', 'StorageClass']
                )
            except Exception as attr_error:
                print(f"Advertencia: No se pudieron obtener atributos adicionales: {str(attr_error)}")
                object_info = {}
            
            s3_data = {
                'file_size': response.get('ContentLength'),
                'last_modified': response.get('LastModified').isoformat() if response.get('LastModified') else None,
                'etag': response.get('ETag'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {}),
                'storage_class': response.get('StorageClass', 'STANDARD'),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'version_id': response.get('VersionId'),
                'checksum': object_info.get('Checksum', {}),
                'creation_date': response.get('LastModified').isoformat() if response.get('LastModified') else None
            }
            
            return s3_data
            
        except self.s3_client.exceptions.NoSuchKey:
            return {'s3_error': 'Archivo no encontrado en S3'}
        except Exception as e:
            return {'s3_error': f'Error accediendo a S3: {str(e)}'}

    def _get_shared_file_info(self, file_key):
        try:
            shared_files = SharedFile.objects.filter(file_key=file_key)
            
            if not shared_files.exists():
                return {
                    'is_shared': False,
                    'shared_count': 0,
                    'shared_with': []
                }
            
            shared_with_users = []
            for shared_file in shared_files:
                shared_with_users.append({
                    'user_id': shared_file.shared_with_user_id,
                    'user_email': shared_file.shared_with_user_email,
                    'shared_at': shared_file.shared_at.isoformat(),
                    'sharing_id': shared_file.id
                })
            
            shared_data = {
                'is_shared': True,
                'shared_count': shared_files.count(),
                'shared_with': shared_with_users
            }
            
            return shared_data
            
        except Exception as e:
            return {'error': f'Error accediendo a base de datos: {str(e)}'}

    def _get_owner_info(self, file_key, user_id=None, user_email=None):
        try:
            shared_file = SharedFile.objects.filter(file_key=file_key).first()
            
            if shared_file:
                owner_info = {
                    'owner_user_email': shared_file.owner_user_email,
                    'file_name': shared_file.file_name,
                }
                return owner_info
            
            elif user_id:
                file_name = file_key.split('/')[-1] if '/' in file_key else file_key
                
                owner_info = {
                    'owner_user_email': user_email or f"{user_id}@gmail.com",
                    'file_name': file_name,
                }
                return owner_info
            
            else:
                return None
            
        except Exception as e:
            return None

    def get_all_files_audit(self, user_id=None, user_email=None):
        try:
            if user_id:
                bucket_name = f"{user_id}-security-project"
            else:
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            
            # Verificar si el bucket existe
            try:
                response = self.s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            except Exception as e:
                return {
                    'error': 'BUCKET_ACCESS_ERROR',
                    'message': f'No se puede acceder al bucket "{bucket_name}": {str(e)}',
                    'bucket_name': bucket_name,
                    'audit_timestamp': datetime.now().isoformat()
                }
            
            # Listar todos los objetos en el bucket
            try:
                response = self.s3_client.list_objects_v2(Bucket=bucket_name)
            except Exception as e:
                return {
                    'error': 'BUCKET_LIST_ERROR',
                    'message': f'Error listando archivos del bucket: {str(e)}',
                    'bucket_name': bucket_name,
                    'audit_timestamp': datetime.now().isoformat()
                }
            
            if 'Contents' not in response:
                return {
                    'message': 'BUCKET_EMPTY',
                    'description': 'El bucket no contiene archivos',
                    'bucket_name': bucket_name,
                    'total_files': 0,
                    'audit_timestamp': datetime.now().isoformat()
                }
            
            audit_results = []
            for obj in response['Contents']:
                file_key = obj['Key']
                # Solo procesar archivos, no carpetas
                if not file_key.endswith('/'):
                    try:
                        audit_info = self.get_file_audit_info(file_key, user_id, user_email)
                        audit_results.append(audit_info)
                    except Exception as e:
                        # Si falla la auditoría de un archivo, continuar con los demás
                        audit_results.append({
                            'file_key': file_key,
                            'error': 'INDIVIDUAL_FILE_ERROR',
                            'message': f'Error en auditoría del archivo: {str(e)}'
                        })
            
            return {
                'files_audit': audit_results,
                'total_files': len(audit_results),
                'bucket_name': bucket_name,
                'audit_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': 'GENERAL_ERROR',
                'message': f'Error obteniendo auditoría de todos los archivos: {str(e)}',
                'audit_timestamp': datetime.now().isoformat()
            } 