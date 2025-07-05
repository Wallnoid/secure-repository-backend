from django.db import models

class CognitoUserManager(models.Manager):
    def get_or_create_for_cognito(self, payload):
        
        user = self.model()  
     
        user.username = payload.get('username', payload.get('cognito:username'))
        user.email = payload.get('email', payload.get('cognito:email'))
        
        user.jwt_payload = payload
        return user

class CognitoUser(models.Model):
    username = models.CharField(max_length=150, blank=True)

    @property
    def is_authenticated(self):
        return True

    objects = CognitoUserManager()

    class Meta:
        managed = False
        app_label = 'aws_auth_service'
