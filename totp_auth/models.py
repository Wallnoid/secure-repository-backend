from django.db import models

# Create your models here.

class TOTPSecret(models.Model):
    user_email = models.EmailField(unique=True)
    secret = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_email} - {self.secret[:4]}..."
