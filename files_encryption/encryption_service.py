"""
Servicio de cifrado para archivos binarios usando AES 128 personalizado
"""

import os
import base64
import secrets
from datetime import datetime
from typing import Union, Tuple
from django.core.files.uploadedfile import UploadedFile
from .aes_encrypt_only import AES128Encrypt


class FileEncryptionService:
    """
    Servicio para cifrar archivos binarios usando implementación AES 128 personalizada
    """
    
    def __init__(self, encryption_key: str = None):
        """
        Inicializar el servicio de cifrado
        
        Args:
            encryption_key: Clave de cifrado (16 caracteres texto o 32 caracteres hexadecimal)
        """
        self.aes_cipher = AES128Encrypt()
        
        if encryption_key:
            # Validar la clave usando el método de la clase AES
            try:
                self.aes_cipher._process_key(encryption_key)
                self.encryption_key = encryption_key
            except ValueError as e:
                raise ValueError(f"Clave de cifrado inválida: {str(e)}")
        else:
            # Obtener clave desde variables de entorno
            self.encryption_key = os.getenv('AES_ENCRYPTION_KEY')
            if not self.encryption_key:
                raise ValueError("No se encontró la clave de cifrado en variables de entorno")
            
            # Validar la clave obtenida
            try:
                self.aes_cipher._process_key(self.encryption_key)
            except ValueError as e:
                raise ValueError(f"Clave de cifrado en variables de entorno inválida: {str(e)}")
        
        # Definir directorio para archivos cifrados
        self.encrypted_files_dir = os.path.join('files_encryption', 'encrypted_files')
        os.makedirs(self.encrypted_files_dir, exist_ok=True)
    
    def encrypt_binary_content(self, binary_content: bytes) -> bytes:
        """
        Cifrar contenido binario directamente
        
        Args:
            binary_content: Contenido binario a cifrar
            
        Returns:
            bytes: Contenido cifrado como bytes
        """
        try:
            # Convertir bytes a string base64 para poder cifrarlo
            base64_content = base64.b64encode(binary_content).decode('utf-8')
            
            # Cifrar usando el algoritmo
            encrypted_bytes = self.aes_cipher.encrypt(base64_content, self.encryption_key)
            
            return encrypted_bytes
            
        except Exception as e:
            raise Exception(f"Error al cifrar el contenido binario: {str(e)}")
    
    def encrypt_file(self, uploaded_file: UploadedFile, metadata: dict = None) -> dict:
        """
        Cifrar archivo binario completo y guardarlo como .bin
        
        Args:
            uploaded_file: Archivo .bin subido desde el frontend
            metadata: Metadatos opcionales del archivo
            
        Returns:
            dict: Resultado del cifrado con información del archivo .bin guardado
        """
        try:
            # Validar que sea un archivo .bin
            if not uploaded_file.name.lower().endswith('.bin'):
                raise ValueError("El archivo debe tener extensión .bin")
            
            # Leer contenido binario del archivo
            binary_content = uploaded_file.read()
            
            # Cifrar el contenido binario
            encrypted_bytes = self.encrypt_binary_content(binary_content)
            
            # Generar nombre único para el archivo cifrado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = os.path.splitext(uploaded_file.name)[0]
            encrypted_filename = f"{original_name}_encrypted_{timestamp}.bin"
            
            # Guardar archivo cifrado como .bin
            encrypted_file_path = os.path.join(self.encrypted_files_dir, encrypted_filename)
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_bytes)
            
            # Preparar respuesta
            result = {
                'encrypted_file_url': f'/encrypted_files/{encrypted_filename}',
                'encrypted_filename': encrypted_filename,
                'original_filename': uploaded_file.name,
                'original_size': len(binary_content),
                'encrypted_size': len(encrypted_bytes),
                'encryption_algorithm': 'AES-128-Binary-Custom',
                'status': 'success',
                'message': 'Archivo .bin cifrado y guardado exitosamente'
            }
            
            # Agregar metadatos si se proporcionan
            if metadata:
                result['metadata'] = metadata
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error al procesar el archivo .bin: {str(e)}",
                'encrypted_file_url': None
            }

    def validate_encrypted_content(self, encrypted_content: str) -> bool:
        """
        Validar que el contenido cifrado sea válido (método legacy)
        
        Args:
            encrypted_content: Contenido cifrado en base64
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        try:
            # Intentar decodificar base64
            base64.b64decode(encrypted_content.encode('utf-8'))
            return True
        except Exception:
            return False
    
    def encrypt_text_content(self, text_content: str) -> str:
        """
        Cifrar el contenido de texto (método legacy para compatibilidad)
        
        Args:
            text_content: Contenido de texto a cifrar
            
        Returns:
            str: Contenido cifrado en base64
        """
        try:
            # Cifrar usando el algoritmo unificado
            encrypted_bytes = self.aes_cipher.encrypt(text_content, self.encryption_key)
            
            # Convertir a base64 para transporte seguro
            encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            
            return encrypted_base64
            
        except Exception as e:
            raise Exception(f"Error al cifrar el contenido: {str(e)}")

    def encrypt_file_from_frontend(self, file_content: str, metadata: dict = None) -> dict:
        """
        Procesar archivo desde el frontend y cifrarlo (método legacy para compatibilidad)
        
        Args:
            file_content: Contenido del archivo como string
            metadata: Metadatos opcionales del archivo
            
        Returns:
            dict: Resultado del cifrado con información adicional
        """
        try:
            # Validar que el contenido no esté vacío
            if not file_content:
                raise ValueError("El contenido del archivo no puede estar vacío")
            
            # Cifrar el contenido
            encrypted_content = self.encrypt_text_content(file_content)
            
            # Preparar respuesta
            result = {
                'encrypted_content': encrypted_content,
                'original_size': len(file_content.encode('utf-8')),
                'encrypted_size': len(encrypted_content.encode('utf-8')),
                'encryption_algorithm': 'AES-128-ECB-Custom',
                'status': 'success',
                'message': 'Archivo cifrado exitosamente'
            }
            
            # Agregar metadatos si se proporcionan
            if metadata:
                result['metadata'] = metadata
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error al procesar el archivo: {str(e)}",
                'encrypted_content': None
            }
    
    def get_encryption_info(self) -> dict:
        """
        Obtener información sobre el servicio de cifrado
        
        Returns:
            dict: Información del servicio
        """
        return {
            'algorithm': 'AES-128-ECB',
            'implementation': 'Custom from scratch - Binary encryption',
            'key_size': '128 bits',
            'key_formats': ['16 caracteres texto', '32 caracteres hexadecimal'],
            'block_size': '128 bits',
            'mode': 'ECB',
            'padding': 'PKCS#7',
            'input_format': 'Binary (.bin files)',
            'output_format': 'Binary (.bin files)',
            'operation': 'Binary file encryption'
        }
    
    @staticmethod
    def generate_aes_key() -> str:
        """
        Generar una clave AES 128 segura
        
        Returns:
            str: Clave de 16 caracteres
        """
        # Generar 16 bytes aleatorios seguros
        key_bytes = secrets.token_bytes(16)
        
        # Convertir a string usando caracteres alfanuméricos
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        key = ''.join(charset[b % len(charset)] for b in key_bytes)
        
        return key 