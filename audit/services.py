import boto3
from django.conf import settings
from shared_files.models import SharedFile
from .models import FileLog, FolderLog
from datetime import datetime
import json
from django.utils import timezone
from django.db import models
from django.db.models import Q, Count
import os


class LogService:
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_agent(request):
        return request.META.get('HTTP_USER_AGENT', '')[:200]
    
    @staticmethod
    def log_file_action(action, file_key, user_id, user_email, bucket_name, request=None, 
                       file_name=None, file_size=None, owner_user_id=None, owner_user_email=None,
                       shared_with_user_id=None, shared_with_user_email=None, old_file_name=None,
                       success=True, error_message=None):
        try:
            ip_address = LogService.get_client_ip(request) if request else None
            user_agent = LogService.get_user_agent(request) if request else None
            
            log_entry = FileLog.objects.create(
                user_id=user_id,
                user_email=user_email,
                action=action,
                file_key=file_key,
                file_name=file_name,
                file_size=file_size,
                bucket_name=bucket_name,
                owner_user_id=owner_user_id,
                owner_user_email=owner_user_email,
                shared_with_user_id=shared_with_user_id,
                shared_with_user_email=shared_with_user_email,
                old_file_name=old_file_name,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message
            )
            return log_entry
        except Exception as e:
            print(f"Error creating file log: {str(e)}")
            return None
    
    @staticmethod
    def log_folder_action(action, folder_key, user_id, user_email, bucket_name, request=None,
                         folder_name=None, old_folder_name=None, parent_folder=None, 
                         success=True, error_message=None):
        try:
            ip_address = LogService.get_client_ip(request) if request else None
            user_agent = LogService.get_user_agent(request) if request else None
            
            log_entry = FolderLog.objects.create(
                user_id=user_id,
                user_email=user_email,
                action=action,
                folder_key=folder_key,
                folder_name=folder_name,
                old_folder_name=old_folder_name,
                parent_folder=parent_folder,
                bucket_name=bucket_name,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error_message=error_message
            )
            return log_entry
        except Exception as e:
            print(f"Error creating folder log: {str(e)}")
            return None


class AuditService:
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
    
    @staticmethod
    def _get_bucket_from_username(username):
        return f"{username}-security-project"
    
    @staticmethod
    def _get_user_file_permissions(username, file_key=None, owner_user_id=None):
        user_bucket = AuditService._get_bucket_from_username(username)
        
        q_filter = Q(bucket_name=user_bucket)
        
        if file_key:
            shared_files = SharedFile.objects.filter(
                Q(owner_user_id=username) | Q(shared_with_user_id=username)
            )
            
            shared_conditions = []
            for shared_file in shared_files:
                if hasattr(shared_file, 'file_key'):
                    shared_file_key = shared_file.file_key
                elif hasattr(shared_file, 'file_name'):
                    shared_file_key = shared_file.file_name
                else:
                    continue
                
                if hasattr(shared_file, 'owner_user_id') and shared_file.owner_user_id:
                    owner_bucket = AuditService._get_bucket_from_username(shared_file.owner_user_id)
                    shared_conditions.append(Q(file_key=shared_file_key, bucket_name=owner_bucket))
            
            for condition in shared_conditions:
                q_filter |= condition
        else:
            shared_files_with_user = SharedFile.objects.filter(shared_with_user_id=username)
            shared_conditions = []
            
            for shared_file in shared_files_with_user:
                if hasattr(shared_file, 'file_key'):
                    shared_file_key = shared_file.file_key
                elif hasattr(shared_file, 'file_name'):
                    shared_file_key = shared_file.file_name
                else:
                    continue
                
                if hasattr(shared_file, 'owner_user_id') and shared_file.owner_user_id:
                    owner_bucket = AuditService._get_bucket_from_username(shared_file.owner_user_id)
                    shared_conditions.append(Q(file_key=shared_file_key, bucket_name=owner_bucket))

            for condition in shared_conditions:
                q_filter |= condition
        
        return q_filter
    
    @staticmethod
    def _get_user_folder_permissions(username, folder_key=None):
        user_bucket = AuditService._get_bucket_from_username(username)
        q_filter = Q(bucket_name=user_bucket)
        
        if folder_key:
            q_filter &= Q(folder_key=folder_key)
        
        return q_filter
    
    @staticmethod
    def get_file_logs(username, file_key=None, action=None, start_date=None, end_date=None, limit=100, owner_user_id=None):
        try:
            queryset = FileLog.objects.filter(
                AuditService._get_user_file_permissions(username, file_key, owner_user_id)
            )
            
            if file_key:
                file_filter = Q(file_key=file_key)
                
                if file_key.endswith('.pdf'):
                    file_key_without_pdf = file_key[:-4]
                    file_filter |= Q(file_key=file_key_without_pdf)
                else:
                    file_key_with_pdf = f"{file_key}.pdf"
                    file_filter |= Q(file_key=file_key_with_pdf)
                
                update_logs = FileLog.objects.filter(
                    AuditService._get_user_file_permissions(username, file_key, owner_user_id),
                    action='UPDATE'
                ).values_list('file_key', 'old_file_name')
                
                for log_file_key, old_file_name in update_logs:
                    if log_file_key == file_key and old_file_name:
                        file_filter |= Q(file_key=old_file_name)
                    
                    if file_key.endswith('.pdf'):
                        file_key_without_pdf = file_key[:-4]
                        if log_file_key == file_key_without_pdf and old_file_name:
                            file_filter |= Q(file_key=old_file_name)
                    else:
                        file_key_with_pdf = f"{file_key}.pdf"
                        if log_file_key == file_key_with_pdf and old_file_name:
                            file_filter |= Q(file_key=old_file_name)
                
                file_name = file_key.split('/')[-1]
                
                if file_name.endswith('.pdf'):
                    file_name_without_pdf = file_name[:-4]
                    file_filter |= Q(old_file_name=file_name) | Q(old_file_name=file_name_without_pdf)
                else:
                    file_name_with_pdf = f"{file_name}.pdf"
                    file_filter |= Q(old_file_name=file_name) | Q(old_file_name=file_name_with_pdf)
                
                renamed_from_logs = FileLog.objects.filter(
                    AuditService._get_user_file_permissions(username, file_key, owner_user_id),
                    action='UPDATE'
                ).filter(
                    Q(old_file_name=file_name) | 
                    Q(old_file_name=file_name[:-4] if file_name.endswith('.pdf') else f"{file_name}.pdf")
                ).values_list('file_key', flat=True)
                
                for renamed_file_key in renamed_from_logs:
                    file_filter |= Q(file_key=renamed_file_key)
                
                queryset = queryset.filter(file_filter)
            
            if action:
                queryset = queryset.filter(action=action)
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            queryset = queryset.order_by('-timestamp')
            
            logs = list(queryset[:limit])
            
            logs_data = []
            for log in logs:
                log_data = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'user_email': log.user_email,
                    'action': log.action,
                    'action_display': log.get_action_display(),
                    'file_key': log.file_key,
                    'file_name': log.file_name,
                    'file_size': log.file_size,
                    'owner_user_id': log.owner_user_id,
                    'owner_user_email': log.owner_user_email,
                    'shared_with_user_id': log.shared_with_user_id,
                    'shared_with_user_email': log.shared_with_user_email,
                    'old_file_name': log.old_file_name,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'timestamp': log.timestamp.isoformat(),
                    'success': log.success,
                    'error_message': log.error_message
                }
                logs_data.append(log_data)
            
            return {
                'success': True,
                'data': logs_data,
                'total_count': queryset.count(),
                'applied_filters': {
                    'username': username,
                    'file_key': file_key,
                    'action': action,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'limit': limit,
                    'owner_user_id': owner_user_id
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Error retrieving file logs: {str(e)}",
                'data': []
            }
    
    @staticmethod
    def get_folder_logs(username, folder_key=None, action=None, start_date=None, end_date=None, limit=100):
        try:
            queryset = FolderLog.objects.filter(
                AuditService._get_user_folder_permissions(username, folder_key)
            )
            
            if folder_key:
                queryset = queryset.filter(folder_key=folder_key)
            
            if action:
                queryset = queryset.filter(action=action)
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            queryset = queryset.order_by('-timestamp')
            
            logs = list(queryset[:limit])
            
            logs_data = []
            for log in logs:
                log_data = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'user_email': log.user_email,
                    'action': log.action,
                    'action_display': log.get_action_display(),
                    'folder_key': log.folder_key,
                    'folder_name': log.folder_name,
                    'old_folder_name': log.old_folder_name,
                    'parent_folder': log.parent_folder,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'timestamp': log.timestamp.isoformat(),
                    'success': log.success,
                    'error_message': log.error_message
                }
                logs_data.append(log_data)
            
            return {
                'success': True,
                'data': logs_data,
                'total_count': queryset.count(),
                'applied_filters': {
                    'username': username,
                    'folder_key': folder_key,
                    'action': action,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'limit': limit
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Error retrieving folder logs: {str(e)}",
                'data': []
            }
    
    @staticmethod
    def get_user_file_stats(username, start_date=None, end_date=None):
        try:
            queryset = FileLog.objects.filter(
                AuditService._get_user_file_permissions(username)
            )
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            action_stats = queryset.values('action').annotate(
                count=Count('action')
            ).order_by('-count')
            
            total_operations = queryset.count()
            successful_operations = queryset.filter(success=True).count()
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
            
            unique_files = queryset.values('file_key').distinct().count()
            
            first_log = queryset.order_by('timestamp').first()
            last_log = queryset.order_by('-timestamp').first()
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'success_rate': round(success_rate, 2),
                'unique_files': unique_files,
                'action_breakdown': list(action_stats),
                'date_range': {
                    'from': first_log.timestamp.isoformat() if first_log else None,
                    'to': last_log.timestamp.isoformat() if last_log else None
                }
            }
        
        except Exception as e:
            return {
                'error': f"Error getting file statistics: {str(e)}"
            }
    
    @staticmethod
    def get_user_folder_stats(username, start_date=None, end_date=None):
        try:
            queryset = FolderLog.objects.filter(
                AuditService._get_user_folder_permissions(username)
            )
            
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
            
            action_stats = queryset.values('action').annotate(
                count=Count('action')
            ).order_by('-count')
            
            total_operations = queryset.count()
            successful_operations = queryset.filter(success=True).count()
            success_rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
            
            unique_folders = queryset.values('folder_key').distinct().count()
            
            first_log = queryset.order_by('timestamp').first()
            last_log = queryset.order_by('-timestamp').first()
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'success_rate': round(success_rate, 2),
                'unique_folders': unique_folders,
                'action_breakdown': list(action_stats),
                'date_range': {
                    'from': first_log.timestamp.isoformat() if first_log else None,
                    'to': last_log.timestamp.isoformat() if last_log else None
                }
            }
        
        except Exception as e:
            return {
                'error': f"Error getting folder statistics: {str(e)}"
            }
    
    @staticmethod
    def get_folder_files_logs(username, folder_key):
        try:
            queryset = FileLog.objects.filter(
                AuditService._get_user_file_permissions(username)
            )
            
            if folder_key and folder_key.strip():
                queryset = queryset.filter(file_key__startswith=folder_key)
            else:
                queryset = queryset.filter(file_key__regex=r'^[^/]+$')
            
            queryset = queryset.order_by('-timestamp')
            
            logs = list(queryset)
            
            logs_data = []
            for log in logs:
                log_data = {
                    'id': log.id,
                    'user_id': log.user_id,
                    'user_email': log.user_email,
                    'action': log.action,
                    'action_display': log.get_action_display(),
                    'file_key': log.file_key,
                    'file_name': log.file_name,
                    'file_size': log.file_size,
                    'owner_user_id': log.owner_user_id,
                    'owner_user_email': log.owner_user_email,
                    'shared_with_user_id': log.shared_with_user_id,
                    'shared_with_user_email': log.shared_with_user_email,
                    'old_file_name': log.old_file_name,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'timestamp': log.timestamp.isoformat(),
                    'success': log.success,
                    'error_message': log.error_message
                }
                logs_data.append(log_data)
            
            stats = AuditService.get_user_file_stats(username)
            
            unique_files = queryset.values('file_key').distinct().count()
            unique_users = queryset.values('user_id').distinct().count()
            
            total_ops = queryset.count()
            successful_ops = queryset.filter(success=True).count()
            success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
            
            first_log = queryset.first()
            last_log = queryset.last()
            
            folder_description = "Root directory" if not folder_key or not folder_key.strip() else f"Folder: {folder_key}"
            
            return {
                'success': True,
                'file_logs': logs_data,
                'summary': {
                    'total_operations': total_ops,
                    'successful_operations': successful_ops,
                    'unique_files': unique_files,
                    'unique_users': unique_users,
                    'success_rate': round(success_rate, 2),
                    'date_range': {
                        'from': first_log.timestamp.isoformat() if first_log else None,
                        'to': last_log.timestamp.isoformat() if last_log else None
                    }
                },
                'folder_key': folder_key,
                'folder_description': folder_description,
                'username': username,
                'audit_timestamp': timezone.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Error retrieving folder files audit: {str(e)}",
                'file_logs': []
            }

    def get_file_audit_info(self, file_key, username):
        try:
            bucket_name = self._get_bucket_from_username(username)
            
            file_exists = self._check_file_exists(bucket_name, file_key)
            if not file_exists:
                rename_info = self._check_if_file_was_renamed(file_key, username)
                if rename_info:
                    return {
                        'error': 'FILE_NOT_FOUND',
                        'message': f'File "{file_key}" does not exist. It may have been renamed.',
                        'file_key': file_key,
                        'rename_info': rename_info,
                        'suggestion': f'Try searching for the current file name: {rename_info.get("current_file_key", "unknown")}',
                        'audit_timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'error': 'FILE_NOT_FOUND',
                        'message': f'File "{file_key}" does not exist',
                        'file_key': file_key,
                        'audit_timestamp': datetime.now().isoformat()
                    }

            s3_metadata = self._get_s3_file_metadata(bucket_name, file_key)
            
            if 's3_error' in s3_metadata:
                return {
                    'error': 'S3_ACCESS_ERROR',
                    'message': f'Error accessing file in S3: {s3_metadata["s3_error"]}',
                    'file_key': file_key,
                    'audit_timestamp': datetime.now().isoformat()
                }
            
            shared_info = self._get_shared_file_info(file_key)
            
            owner_info = self._get_owner_info(file_key, username, None)
            
            recent_logs = self._get_recent_file_logs(file_key, username, limit=10)
            
            is_shared_file = False
            if isinstance(shared_info, list) and len(shared_info) > 0:
                for share in shared_info:
                    if share.get('owner_user_id') == username:
                        is_shared_file = True
                        break

            return {
                'file_key': file_key,
                'file_metadata': s3_metadata,
                'shared_info': shared_info,
                'owner_info': owner_info,
                'recent_logs': recent_logs,
                'is_shared_file': is_shared_file,
                'audit_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': 'GENERAL_ERROR',
                'message': f'Error getting file audit info: {str(e)}',
                'file_key': file_key,
                'audit_timestamp': datetime.now().isoformat()
            }

    def _check_file_exists(self, bucket_name, file_key):
        try:
            try:
                self.s3_client.head_object(Bucket=bucket_name, Key=file_key)
                return True
            except:
                pass
            
            if not file_key.endswith('.pdf'):
                try:
                    self.s3_client.head_object(Bucket=bucket_name, Key=f"{file_key}.pdf")
                    return True
                except:
                    pass
            
            elif file_key.endswith('.pdf'):
                try:
                    file_key_without_pdf = file_key[:-4]
                    self.s3_client.head_object(Bucket=bucket_name, Key=file_key_without_pdf)
                    return True
                except:
                    pass
            
            return False
        except Exception as e:
            return False

    def _get_s3_file_metadata(self, bucket_name, file_key):
        try:
            try:
                response = self.s3_client.head_object(Bucket=bucket_name, Key=file_key)
                return self._format_s3_metadata(response)
            except:
                pass
            
            if not file_key.endswith('.pdf'):
                try:
                    response = self.s3_client.head_object(Bucket=bucket_name, Key=f"{file_key}.pdf")
                    return self._format_s3_metadata(response)
                except:
                    pass
            
            elif file_key.endswith('.pdf'):
                try:
                    file_key_without_pdf = file_key[:-4]
                    response = self.s3_client.head_object(Bucket=bucket_name, Key=file_key_without_pdf)
                    return self._format_s3_metadata(response)
                except:
                    pass
            
            return {'s3_error': 'File not found'}
        except Exception as e:
            return {'s3_error': str(e)}
    
    def _format_s3_metadata(self, response):
        return {
            'last_modified': response.get('LastModified'),
            'content_length': response.get('ContentLength'),
            'content_type': response.get('ContentType'),
            'etag': response.get('ETag'),
            'metadata': response.get('Metadata', {})
        }

    def _get_shared_file_info(self, file_key):
        try:
            search_keys = [file_key]
            if file_key.endswith('.pdf'):
                search_keys.append(file_key[:-4])
            
            shared_files = SharedFile.objects.filter(file_key__in=search_keys)
            if shared_files.exists():
                return [
                    {
                        'shared_with_user_id': sf.shared_with_user_id,
                        'shared_with_user_email': sf.shared_with_user_email,
                        'shared_at': sf.shared_at.isoformat(),
                        'owner_user_id': sf.owner_user_id,
                        'owner_user_email': sf.owner_user_email
                    } for sf in shared_files
                ]
            return []
        except Exception as e:
            return {'error': f'Error getting shared info: {str(e)}'}

    def _get_owner_info(self, file_key, user_id, user_email):
        try:
            if user_id:
                if not user_email or user_email.endswith('@example.com'):
                    real_email = CognitoService.get_user_email(user_id)
                else:
                    real_email = user_email
                
                return {
                    'current_user_id': user_id,
                    'current_user_email': real_email,
                    'is_owner': True
                }
            return {'error': 'No user information provided'}
        except Exception as e:
            return {'error': f'Error getting owner info: {str(e)}'}

    def _check_if_file_was_renamed(self, file_key, username):
        try:
            file_name = file_key.split('/')[-1]
            
            if file_name.endswith('.pdf'):
                file_name_without_pdf = file_name[:-4]
                search_names = [file_name, file_name_without_pdf]
            else:
                file_name_with_pdf = f"{file_name}.pdf"
                search_names = [file_name, file_name_with_pdf]
            
            renamed_to_logs = FileLog.objects.filter(
                AuditService._get_user_file_permissions(username),
                action='UPDATE',
                old_file_name__in=search_names
            ).order_by('-timestamp').first()
            
            if renamed_to_logs:
                return {
                    'was_renamed': True,
                    'old_file_key': file_key,
                    'current_file_key': renamed_to_logs.file_key,
                    'renamed_at': renamed_to_logs.timestamp.isoformat(),
                    'renamed_by': renamed_to_logs.user_id
                }
                
            file_key_variants = [file_key]
            if file_key.endswith('.pdf'):
                file_key_variants.append(file_key[:-4])
            else:
                file_key_variants.append(f"{file_key}.pdf")
            
            renamed_from_logs = FileLog.objects.filter(
                AuditService._get_user_file_permissions(username),
                action='UPDATE',
                file_key__in=file_key_variants
            ).order_by('-timestamp').first()
            
            if renamed_from_logs and renamed_from_logs.old_file_name:
                old_file_key = f"{'/'.join(file_key.split('/')[:-1])}/{renamed_from_logs.old_file_name}"
                return {
                    'was_renamed': True,
                    'old_file_key': old_file_key,
                    'current_file_key': file_key,
                    'renamed_at': renamed_from_logs.timestamp.isoformat(),
                    'renamed_by': renamed_from_logs.user_id
                }
            
            return None
        except Exception as e:
            return None

    def _get_recent_file_logs(self, file_key, username, limit=10):
        try:
            logs_result = AuditService.get_file_logs(
                username=username,
                file_key=file_key,
                limit=limit
            )
            
            if logs_result.get('success'):
                return logs_result.get('data', [])
            else:
                return []
        except Exception as e:
            return []

    def get_all_files_audit(self, username):
        try:
            bucket_name = self._get_bucket_from_username(username)
            
            try:
                response = self.s3_client.list_objects(Bucket=bucket_name)
            except Exception as e:
                return {
                    'error': 'BUCKET_ACCESS_ERROR',
                    'message': f'Error accessing bucket: {str(e)}',
                    'audit_timestamp': datetime.now().isoformat()
                }

            if 'Contents' not in response:
                return {
                    'message': 'BUCKET_EMPTY',
                    'files_audit': [],
                    'total_files': 0,
                    'audit_timestamp': datetime.now().isoformat()
                }

            audit_results = []

            for obj in response['Contents']:
                file_key = obj['Key']
                if not file_key.endswith('/'):
                    try:
                        audit_info = self.get_file_audit_info(file_key, username)
                        audit_results.append(audit_info)
                    except Exception as e:
                        audit_results.append({
                            'file_key': file_key,
                            'error': 'INDIVIDUAL_FILE_ERROR',
                            'message': f'Error in file audit: {str(e)}'
                        })
            
            return {
                'files_audit': audit_results,
                'total_files': len(audit_results),
                'username': username,
                'audit_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': 'GENERAL_ERROR',
                'message': f'Error getting audit for all files: {str(e)}',
                'username': username,
                'audit_timestamp': datetime.now().isoformat()
            }


class CognitoService:
    
    @staticmethod
    def get_user_email(user_id):
        try:
            region_name = os.getenv('COGNITO_AWS_REGION', 'us-east-2')
            user_pool_id = os.getenv('COGNITO_USER_POOL')
            
            if not user_pool_id:
                return f'{user_id}@example.com'
            
            client = boto3.client('cognito-idp', region_name=region_name)
            
            try:
                response = client.admin_get_user(
                    UserPoolId=user_pool_id,
                    Username=user_id
                )
                
                for attr in response['UserAttributes']:
                    if attr['Name'] == 'email':
                        return attr['Value']
                        
                return f'{user_id}@example.com'
                
            except client.exceptions.UserNotFoundException:
                return f'{user_id}@example.com'
                
        except Exception as e:
            print(f"Error getting user email from Cognito: {str(e)}")
            return f'{user_id}@example.com'