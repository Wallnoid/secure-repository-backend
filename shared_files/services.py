# GUARDAR, EDITAR, REMOVER Y RECUPERAR DE LA BD

from shared_files.models import SharedFile


class SharedFileService:
    def __init__(self):
        self.model = SharedFile

    def save(self, shared_file):
        return self.model.objects.create(**shared_file)


    def update(self, shared_file):
        return self.model.objects.filter(id=shared_file.id).update(**shared_file)
    
    def update_file_key(self, file_key, new_file_key):
        
       
        if '/' in file_key:
            file_name = file_key.split('/')[-1]
            return self.model.objects.filter(file_key=file_key).update(file_key=new_file_key, file_name=file_name)
        else:
            return self.model.objects.filter(file_key=file_key).update(file_key=new_file_key)
    
    def update_folder_key(self, folder_key, new_folder_key):
        files = self.model.objects.filter(file_key__contains=folder_key)
        
        for file in files:
            if folder_key in file.file_key:
                new_file_key = file.file_key.replace(folder_key, new_folder_key)
                self.model.objects.filter(id=file.id).update(file_key=new_file_key)
        
        return self.model.objects.filter(folder_key=folder_key).update(folder_key=new_folder_key)


    def delete(self, file_key):
        return self.model.objects.filter(file_key=file_key).delete()
    
    def delete_folder(self, folder_key):
        files_with_folder = self.model.objects.filter(file_key__contains=folder_key)
        files_with_folder.delete()
        
        return self.model.objects.filter(folder_key=folder_key).delete()


    def get_by_shared_with_user_id(self, shared_with_user_id ):
        return self.model.objects.filter(shared_with_user_id=shared_with_user_id).all()
    
    def get_by_file_key(self, file_key, owner_user_id):
        return self.model.objects.filter(file_key=file_key, owner_user_id=owner_user_id).all()
    
    def get_by_owner_user_id(self, owner_user_id):
        return self.model.objects.filter(owner_user_id=owner_user_id).all()


    def get_all(self):
        return self.model.objects.all()


