"""
Serializers para el servicio de cifrado de archivos
"""

from rest_framework import serializers


class EncryptFileSerializer(serializers.Serializer):
    """
    Serializer para validar la entrada de cifrado de archivos binarios
    """
    file = serializers.FileField(
        required=True,
        help_text="Archivo .bin a cifrar"
    )
    
    description = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Descripción del archivo (opcional)"
    )
    
    def validate_file(self, value):
        """
        Validar el archivo binario
        """
        if not value:
            raise serializers.ValidationError("El archivo no puede estar vacío")
        
        # Validar extensión .bin
        if not value.name.lower().endswith('.bin'):
            raise serializers.ValidationError("El archivo debe tener extensión .bin")
        
        # Validar que no sea demasiado grande (límite de 50MB para archivos binarios)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("El archivo es demasiado grande (máximo 50MB)")
        
        # Validar que tenga contenido
        if value.size == 0:
            raise serializers.ValidationError("El archivo no puede estar vacío")
        
        return value


class EncryptionResponseSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de cifrado exitoso de archivos binarios
    """
    encrypted_file_url = serializers.CharField(help_text="URL del archivo .bin cifrado generado")
    encrypted_filename = serializers.CharField(help_text="Nombre del archivo .bin cifrado")
    original_filename = serializers.CharField(help_text="Nombre del archivo .bin original")
    original_size = serializers.IntegerField(help_text="Tamaño original del archivo en bytes")
    encrypted_size = serializers.IntegerField(help_text="Tamaño del archivo cifrado en bytes")
    encryption_algorithm = serializers.CharField(help_text="Algoritmo utilizado")
    status = serializers.CharField(help_text="Estado de la operación")
    message = serializers.CharField(help_text="Mensaje informativo")
    metadata = serializers.DictField(required=False, help_text="Metadatos del archivo")


class EncryptionInfoSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de información de cifrado
    """
    algorithm = serializers.CharField()
    implementation = serializers.CharField()
    key_size = serializers.CharField()
    block_size = serializers.CharField()
    mode = serializers.CharField()
    padding = serializers.CharField()
    encoding = serializers.CharField()
    operation = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer para respuestas de error
    """
    status = serializers.CharField()
    message = serializers.CharField()
    error_code = serializers.CharField(required=False)
    
    class Meta:
        ref_name = 'EncryptionErrorResponse' 