
from django.urls import path
from .views import GetDocsView

urlpatterns = [
    path('all-docs/', GetDocsView.get_all, name='all_docs'),
    path('get-doc/', GetDocsView.get, name='get_doc'),
]


