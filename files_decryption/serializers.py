"""
Serializers para el servicio de descifrado de archivos binarios
"""

import json
from rest_framework import serializers


class DecryptFileSerializer(serializers.Serializer):
    """
    Serializer para validar la entrada de descifrado de archivos binarios
    """
    encrypted_file = serializers.FileField(
        required=True,
        help_text="Archivo .bin cifrado a descifrar"
    )
    
    additional_info = serializers.CharField(
        required=False,
        help_text="Información adicional sobre el archivo cifrado (opcional, formato JSON)"
    )
    
    def validate_encrypted_file(self, value):
        """
        Validar el archivo binario cifrado
        """
        if not value:
            raise serializers.ValidationError("El archivo cifrado no puede estar vacío")
        
        # Validar que tenga contenido
        if value.size == 0:
            raise serializers.ValidationError("El archivo cifrado no puede estar vacío")
        
        # Validar extensión .bin
        if not value.name.lower().endswith('.bin'):
            raise serializers.ValidationError("El archivo debe tener extensión .bin")
        
        # Validar que no sea demasiado grande (límite de 50MB)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("El archivo es demasiado grande (máximo 50MB)")
        
        return value
    
    def validate_additional_info(self, value):
        """
        Validar y convertir additional_info de JSON string a dict
        """
        if not value:
            return None
        
        try:
            # Intentar parsear el JSON
            return json.loads(value)
        except json.JSONDecodeError:
            raise serializers.ValidationError("additional_info debe ser un JSON válido")


class ValidateEncryptedContentSerializer(serializers.Serializer):
    """
    Serializer para validar contenido cifrado sin descifrarlo
    """
    encrypted_content = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Contenido cifrado en base64 a validar"
    )
    
    def validate_encrypted_content(self, value):
        """
        Validar el contenido cifrado
        """
        if not value or not value.strip():
            raise serializers.ValidationError("El contenido cifrado no puede estar vacío")
        
        return value


class EstimateSizeSerializer(serializers.Serializer):
    """
    Serializer para estimar el tamaño del contenido descifrado
    """
    encrypted_content = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Contenido cifrado en base64"
    )
    
    def validate_encrypted_content(self, value):
        """
        Validar el contenido cifrado
        """
        if not value or not value.strip():
            raise serializers.ValidationError("El contenido cifrado no puede estar vacío")
        
        return value


class DecryptionResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de descifrado exitoso de archivos binarios
    """
    decrypted_file_url = serializers.CharField(help_text="URL del archivo .bin descifrado generado")
    decrypted_filename = serializers.CharField(help_text="Nombre del archivo .bin descifrado")
    original_filename = serializers.CharField(help_text="Nombre del archivo .bin original")
    original_size = serializers.IntegerField(help_text="Tamaño original del contenido en bytes")
    encrypted_size = serializers.IntegerField(help_text="Tamaño del contenido cifrado en bytes")
    decryption_algorithm = serializers.CharField(help_text="Algoritmo utilizado")
    status = serializers.CharField(help_text="Estado de la operación")
    message = serializers.CharField(help_text="Mensaje informativo")
    additional_info = serializers.DictField(required=False, help_text="Información adicional")


class ValidationResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de validación de contenido cifrado
    """
    is_valid = serializers.BooleanField(help_text="Si el contenido es válido")
    status = serializers.CharField(help_text="Estado de la validación")
    message = serializers.CharField(help_text="Mensaje informativo")
    format_details = serializers.DictField(required=False, help_text="Detalles del formato")


class SizeEstimationResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de estimación de tamaño
    """
    encrypted_size_bytes = serializers.IntegerField(help_text="Tamaño cifrado en bytes")
    encrypted_size_base64 = serializers.IntegerField(help_text="Tamaño cifrado en base64")
    estimated_min_decrypted_size = serializers.IntegerField(help_text="Tamaño mínimo estimado descifrado")
    estimated_max_decrypted_size = serializers.IntegerField(help_text="Tamaño máximo estimado descifrado")
    total_blocks = serializers.IntegerField(help_text="Total de bloques AES")
    status = serializers.CharField(help_text="Estado de la estimación")


class DecryptionInfoSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de información de descifrado
    """
    algorithm = serializers.CharField()
    implementation = serializers.CharField()
    key_size = serializers.CharField()
    block_size = serializers.CharField()
    mode = serializers.CharField()
    padding = serializers.CharField()
    encoding = serializers.CharField()
    operation = serializers.CharField()


class VerificationResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de verificación del servicio
    """
    status = serializers.CharField()
    message = serializers.CharField()
    validation_test = serializers.BooleanField()
    algorithm_info = serializers.DictField()


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer para respuestas de error
    """
    status = serializers.CharField()
    message = serializers.CharField()
    error_code = serializers.CharField(required=False)
    
    class Meta:
        ref_name = 'DecryptionErrorResponse' 