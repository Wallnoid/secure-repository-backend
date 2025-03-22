crear un entorno: py -m venv venv

activar entorno .\venv\Scripts\Activate

configurar para que funcione en powershell:Set-ExecutionPolicy Unrestricted -Scope CurrentUser

desactivar entorno:deactivate

crear archivo de dependencias:  pip freeze > requirements.txt

construir contenedor: docker build -t proyecto

Ejecutar contenedor:  docker run -p 8000:8000 carpeta/proyecto

url:http://127.0.0.1:8000/

correr modo dev y segundo plano (el path dedbe estar en minusculas): docker run -v -d C:/users/asus/workspace/secure-repository-backend/:/app -p 8000:8000 WorkSpace/secure-repository-backend

ver logs: docker logs --follow [id]

ver contenedores: docker ps

ver imagenes: docker images

entrar a la consola de la imagen: docker exec -it {id} /bin/sh
