# GUARDAR, EDITAR, REMOVER Y RECUPERAR DE LA BD

from shared_files.models import SharedFile
from django.db.models import Func, F, Value


class SharedFileService:
    def __init__(self):
        self.model = SharedFile

    def save(self, shared_file):
        return self.model.objects.create(**shared_file)


    def update(self, shared_file):
        return self.model.objects.filter(id=shared_file.id).update(**shared_file)
    
    def update_file_key(self, file_key, new_file_key):
        
       
        if '/' in file_key:
            file_name = new_file_key.split('/')[-1]
            return self.model.objects.filter(file_key=file_key).update(file_key=new_file_key + '.pdf', file_name=file_name+ '.pdf')
        else:
            return self.model.objects.filter(file_key=file_key).update(file_key=new_file_key + ".pdf", file_name=new_file_key + ".pdf")
    
    def update_folder_key(self, folder_key, new_folder_key):
        
        updated_count = self.model.objects.filter(file_key__contains=folder_key).update(
        file_key=Func(
            F('file_key'),
            Value(folder_key),
            Value(new_folder_key),
            function='REPLACE'
            )
        )
        
        return updated_count
        

    def delete(self, id):
        return self.model.objects.filter(id=id).delete()
    
    def delete_by_file_key(self, file_key):
        return self.model.objects.filter(file_key=file_key).delete()
        
    
    def delete_folder(self, folder_key):
        files_with_folder = self.model.objects.filter(file_key__contains=folder_key)
        
        return files_with_folder.delete()
    
    
    def is_the_same_shared_file(self, file_key, owner_user_id, shared_with_user_id):
        return self.model.objects.filter(file_key=file_key, owner_user_id=owner_user_id, shared_with_user_id=shared_with_user_id).exists() 

    def get_by_id(self, id):
        
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def get_by_shared_with_user_id(self, shared_with_user_id ):
        return self.model.objects.filter(shared_with_user_id=shared_with_user_id).all()
    
    def get_by_file_key(self, file_key, owner_user_id):
        return self.model.objects.filter(file_key=file_key, owner_user_id=owner_user_id).all()
    
    def get_by_owner_user_id(self, owner_user_id):
        return self.model.objects.filter(owner_user_id=owner_user_id).all()


    def get_all(self):
        return self.model.objects.all()


