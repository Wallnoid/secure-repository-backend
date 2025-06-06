"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from aws_files_api.urls import urlfilepatterns as aws_urls
from aws_files_api.urls import urlFolderpatterns as aws_urls_folders
from shared_files.urls import urlpatterns as shared_files_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Security Project API",
      default_version='v1',
      description="API para el proyecto de seguridad",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="wulli.mu28@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),

   
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('files/', include(aws_urls)),
        path('folders/', include(aws_urls_folders)),
        path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('shared-files/', include(shared_files_urls)),
        ])),
]


