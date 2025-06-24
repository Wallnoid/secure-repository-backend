from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError

# Create your views here.

class CognitoUserListView(APIView):
    def get(self, request):
        try:
            # Obtener configuración desde variables de entorno
            region_name = os.getenv('COGNITO_AWS_REGION', 'us-east-2')
            user_pool_id = os.getenv('COGNITO_USER_POOL')
            
            if not user_pool_id:
                return Response(
                    {'error': 'COGNITO_USER_POOL_ID no está configurado en las variables de entorno'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Crear cliente de Cognito
            client = boto3.client('cognito-idp', region_name=region_name)
            
            users = []
            paginator = client.get_paginator('list_users')
            
            for page in paginator.paginate(UserPoolId=user_pool_id):
                for user in page['Users']:
                    user_id = user['Username']
                    email = None
                    for attr in user['Attributes']:
                        if attr['Name'] == 'email':
                            email = attr['Value']
                            break
                    users.append({'id': user_id, 'email': email})
            
            return Response({
                'users': users,
                'total_count': len(users)
            })
            
        except NoCredentialsError:
            return Response(
                {'error': 'No se encontraron credenciales de AWS. Configura AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'AccessDeniedException':
                return Response(
                    {'error': f'Acceso denegado: {error_message}. Verifica los permisos de IAM.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            elif error_code == 'ResourceNotFoundException':
                return Response(
                    {'error': f'User Pool no encontrado: {error_message}. Verifica el COGNITO_USER_POOL_ID.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'error': f'Error de AWS: {error_message}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
