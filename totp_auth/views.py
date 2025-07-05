from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import TOTPSecret
import pyotp
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import qrcode
import io
import boto3
from django.core.files.base import ContentFile

# Create your views here.

class GenerateTOTPSecretView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Genera el otpauth_url para configurar TOTP (2FA) en una app de autenticación.",
        responses={
            200: openapi.Response(
                description="otpauth_url generado correctamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'otpauth_url': openapi.Schema(type=openapi.TYPE_STRING, description="URL para apps de autenticación"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje informativo")
                    }
                )
            ),
            401: 'No autorizado',
        },
        tags=['TOTP']
    )
    def post(self, request):
        user_email = request.user.email
        # Buscar si ya existe
        totp_obj, created = TOTPSecret.objects.get_or_create(user_email=user_email)
        if created:
            # Generar nueva clave secreta
            secret = pyotp.random_base32()
            totp_obj.secret = secret
            totp_obj.save()
        else:
            secret = totp_obj.secret
        # Generar URI para apps como Google Authenticator
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user_email, issuer_name="SecureRepository")
        return Response({
            'secret': secret,
            'otpauth_url': totp_uri,
            'message': 'Escanea este QR en tu app de autenticación.'
        })

class ValidateTOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Valida un código TOTP generado por una app de autenticación.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['code'],
            properties={
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="Código TOTP de 6 dígitos")
            }
        ),
        responses={
            200: openapi.Response(
                description="Código TOTP válido",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Código TOTP inválido",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: 'No autorizado',
        },
        tags=['TOTP']
    )
    def post(self, request):
        user_email = request.user.email
        code = request.data.get('code')
        try:
            totp_obj = TOTPSecret.objects.get(user_email=user_email)
        except TOTPSecret.DoesNotExist:
            return Response({'error': 'No existe clave TOTP para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
        totp = pyotp.TOTP(totp_obj.secret)
        if totp.verify(code):
            return Response({'message': 'Código TOTP válido.'})
        else:
            return Response({'error': 'Código TOTP inválido.'}, status=status.HTTP_400_BAD_REQUEST)

class SendTOTPQRView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Genera el QR de TOTP y lo envía por email usando AWS SES al email del usuario autenticado.",
        responses={
            200: openapi.Response(
                description="QR enviado correctamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Error en la solicitud",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: 'No autorizado',
        },
        tags=['TOTP']
    )
    def post(self, request):
        return Response({'error': 'Funcionalidad de envío de correo deshabilitada.'}, status=status.HTTP_400_BAD_REQUEST)
