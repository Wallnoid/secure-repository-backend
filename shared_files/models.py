from django.db import models

class SharedFile(models.Model):
    id = models.AutoField(primary_key=True)
    owner_user_id = models.CharField(max_length=255)
    owner_user_email = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=255)
    file_key = models.TextField()
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    shared_with_user_id = models.CharField(max_length=255)
    shared_with_user_email = models.CharField(max_length=255)
    shared_at = models.DateTimeField(auto_now_add=True)
    can_view = models.BooleanField(default=True)
    can_download = models.BooleanField(default=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.owner_user_id} compartió {self.file_key} con {self.shared_with_user_id}"
