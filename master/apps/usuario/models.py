from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    
    def __str__(self):
        nombre = f"{self.first_name} {self.last_name}".strip()
        return nombre if nombre else self.username
