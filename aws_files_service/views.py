
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .services import AWSFileService

file_service = AWSFileService()

class GetDocsView(APIView):
    
    @api_view(['GET'])
    def get(self,):
        try:
            documento = file_service.get_file()
            return Response(documento, content_type='application/octet-stream', status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @api_view(['GET'])    
    def get_all(self):
        try:
            documentos = file_service.get_all_files()
            return Response(documentos, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class FirmarDocumentoView(APIView):
#     def post(self, request, archivo_key):
#         usuario = request.user  # Suponiendo que ya estás manejando autenticación
#         try:
#             firma_key = file_service.firmar_documento(archivo_key, usuario)
#             return Response({"mensaje": "Documento firmado", "archivo_firmado_key": firma_key}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
