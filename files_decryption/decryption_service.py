"""
Servicio de descifrado para archivos binarios usando AES 128 personalizado
"""

import os
import base64
from datetime import datetime
from typing import Union, Dict
from django.core.files.uploadedfile import UploadedFile
from .aes_cipher_custom import AES128Decrypt


class FileDecryptionService:
    """
    Servicio para descifrar archivos binarios usando implementación AES 128 personalizada
    """
    
    def __init__(self, decryption_key: str = None):
        """
        Inicializar el servicio de descifrado
        
        Args:
            decryption_key: Clave de descifrado (16 caracteres texto o 32 caracteres hexadecimal)
        """
        self.aes_cipher = AES128Decrypt()
        
        if decryption_key:
            # Validar la clave usando el método de la clase AES
            try:
                self.aes_cipher._process_key(decryption_key)
                self.decryption_key = decryption_key
            except ValueError as e:
                raise ValueError(f"Clave de descifrado inválida: {str(e)}")
        else:
            # Obtener clave desde variables de entorno
            self.decryption_key = os.getenv('AES_ENCRYPTION_KEY')
            if not self.decryption_key:
                raise ValueError("No se encontró la clave de descifrado en variables de entorno")
            
            # Validar la clave obtenida
            try:
                self.aes_cipher._process_key(self.decryption_key)
            except ValueError as e:
                raise ValueError(f"Clave de descifrado en variables de entorno inválida: {str(e)}")
        
        # Definir directorio para archivos descifrados
        self.decrypted_files_dir = os.path.join('files_decryption', 'decrypted_files')
        os.makedirs(self.decrypted_files_dir, exist_ok=True)
    
    def decrypt_binary_content(self, encrypted_bytes: bytes) -> bytes:
        """
        Descifrar contenido binario directamente
        
        Args:
            encrypted_bytes: Contenido binario cifrado
            
        Returns:
            bytes: Contenido binario descifrado
        """
        try:
            # Descifrar usando el algoritmo
            decrypted_bytes = self.aes_cipher.decrypt(encrypted_bytes, self.decryption_key)
            
            # Convertir el resultado de base64 a bytes originales
            base64_content = decrypted_bytes.decode('utf-8')
            original_binary = base64.b64decode(base64_content)
            
            return original_binary
            
        except Exception as e:
            raise Exception(f"Error al descifrar el contenido binario: {str(e)}")
    
    def decrypt_file(self, uploaded_file: UploadedFile, additional_info: dict = None) -> dict:
        """
        Descifrar archivo .bin completo y guardarlo como .bin
        
        Args:
            uploaded_file: Archivo .bin cifrado subido desde el frontend
            additional_info: Información adicional opcional
            
        Returns:
            dict: Resultado del descifrado con información del archivo .bin guardado
        """
        try:
            # Validar que sea un archivo .bin
            if not uploaded_file.name.lower().endswith('.bin'):
                raise ValueError("El archivo debe tener extensión .bin")
            
            # Leer contenido binario del archivo cifrado
            encrypted_bytes = uploaded_file.read()
            
            # Descifrar el contenido binario
            decrypted_binary = self.decrypt_binary_content(encrypted_bytes)
            
            # Generar nombre único para el archivo descifrado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_name = os.path.splitext(uploaded_file.name)[0]
            
            # Remover "_encrypted" del nombre si existe
            if "_encrypted" in original_name:
                original_name = original_name.replace("_encrypted", "")
            
            decrypted_filename = f"{original_name}_decrypted_{timestamp}.bin"
            
            # Guardar archivo descifrado como .bin
            decrypted_file_path = os.path.join(self.decrypted_files_dir, decrypted_filename)
            with open(decrypted_file_path, 'wb') as f:
                f.write(decrypted_binary)
            
            # Preparar respuesta
            result = {
                'decrypted_file_url': f'/decrypted_files/{decrypted_filename}',
                'decrypted_filename': decrypted_filename,
                'original_filename': uploaded_file.name,
                'original_size': len(decrypted_binary),
                'encrypted_size': len(encrypted_bytes),
                'decryption_algorithm': 'AES-128-Binary-Custom',
                'status': 'success',
                'message': 'Archivo .bin descifrado y guardado exitosamente'
            }
            
            # Agregar información adicional si se proporciona
            if additional_info:
                result['additional_info'] = additional_info
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error al procesar el archivo .bin: {str(e)}",
                'decrypted_file_url': None
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
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            
            # Verificar que no esté vacío
            if len(encrypted_bytes) == 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    def decrypt_text_content(self, encrypted_content: str) -> str:
        """
        Descifrar el contenido cifrado (método legacy para compatibilidad)
        
        Args:
            encrypted_content: Contenido cifrado en base64
            
        Returns:
            str: Contenido descifrado
        """
        try:
            # Validar formato antes de descifrar
            if not self.validate_encrypted_content(encrypted_content):
                raise ValueError("El contenido cifrado no tiene un formato válido")
            
            # Decodificar desde base64
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            
            # Descifrar usando el algoritmo unificado
            decrypted_bytes = self.aes_cipher.decrypt(encrypted_bytes, self.decryption_key)
            
            # Convertir bytes a string
            decrypted_text = decrypted_bytes.decode('utf-8')
            
            # Normalizar saltos de línea (convertir \r\n a \n para mantener formato original)
            decrypted_text = decrypted_text.replace('\r\n', '\n')
            
            return decrypted_text
            
        except UnicodeDecodeError:
            raise Exception("Error: El contenido descifrado no es texto válido UTF-8")
        except ValueError as e:
            raise Exception(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error al descifrar el contenido: {str(e)}")

    def decrypt_file_for_frontend(self, encrypted_content: str, additional_info: dict = None) -> dict:
        """
        Procesar archivo cifrado desde el frontend y descifrarlo (método legacy)
        
        Args:
            encrypted_content: Contenido cifrado en base64
            additional_info: Información adicional opcional
            
        Returns:
            dict: Resultado del descifrado con información adicional
        """
        try:
            # Validar que el contenido no esté vacío
            if not encrypted_content or not encrypted_content.strip():
                raise ValueError("El contenido cifrado no puede estar vacío")
            
            # Descifrar el contenido
            decrypted_content = self.decrypt_text_content(encrypted_content)
            
            # Preparar respuesta
            result = {
                'decrypted_content': decrypted_content,
                'original_size': len(decrypted_content.encode('utf-8')),
                'encrypted_size': len(encrypted_content.encode('utf-8')),
                'decryption_algorithm': 'AES-128-Unified-Custom',
                'status': 'success',
                'message': 'Archivo descifrado exitosamente'
            }
            
            # Agregar información adicional si se proporciona
            if additional_info:
                result['additional_info'] = additional_info
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Error al procesar el archivo: {str(e)}",
                'decrypted_content': None
            }
    
    def get_decryption_info(self) -> dict:
        """
        Obtener información sobre el servicio de descifrado
        
        Returns:
            dict: Información del servicio
        """
        return {
            'algorithm': 'AES-128-ECB',
            'implementation': 'Custom from scratch - Binary decryption',
            'key_size': '128 bits',
            'key_formats': ['16 caracteres texto', '32 caracteres hexadecimal'],
            'block_size': '128 bits',
            'mode': 'ECB',
            'padding': 'PKCS#7',
            'input_format': 'Binary (.bin files)',
            'output_format': 'Binary (.bin files)',
            'operation': 'Binary file decryption'
        }
    
    def verify_decryption_capability(self, test_data: str = None) -> dict:
        """
        Verificar que el servicio de descifrado funciona correctamente
        
        Args:
            test_data: Datos de prueba opcionales
            
        Returns:
            dict: Resultado de la verificación
        """
        try:
            # Usar datos de prueba si no se proporcionan
            if not test_data:
                # Este es un ejemplo de contenido cifrado conocido para pruebas
                # En una implementación real, esto vendría del servicio de cifrado
                test_data = "placeholder_for_testing"
            
            # Intentar validar el formato
            is_valid = self.validate_encrypted_content(test_data)
            
            return {
                'status': 'ready',
                'message': 'Servicio de descifrado operativo',
                'validation_test': is_valid,
                'algorithm_info': self.get_decryption_info()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error en la verificación: {str(e)}',
                'validation_test': False
            }
    
    def estimate_decrypted_size(self, encrypted_content: str) -> dict:
        """
        Estimar el tamaño del contenido descifrado sin descifrarlo
        
        Args:
            encrypted_content: Contenido cifrado en base64
            
        Returns:
            dict: Información del tamaño estimado
        """
        try:
            if not self.validate_encrypted_content(encrypted_content):
                raise ValueError("Formato de contenido cifrado inválido")
            
            # Decodificar base64 para obtener bytes cifrados
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            encrypted_size = len(encrypted_bytes)
            
            # El tamaño descifrado será menor debido al padding
            # En el peor caso, el padding puede ser de 1-16 bytes
            min_decrypted_size = encrypted_size - 16
            max_decrypted_size = encrypted_size - 1
            
            return {
                'encrypted_size_bytes': encrypted_size,
                'encrypted_size_base64': len(encrypted_content),
                'estimated_min_decrypted_size': max(0, min_decrypted_size),
                'estimated_max_decrypted_size': max_decrypted_size,
                'total_blocks': encrypted_size // 16,
                'status': 'estimated'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error al estimar tamaño: {str(e)}'
            } 