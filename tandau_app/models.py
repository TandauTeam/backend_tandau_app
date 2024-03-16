from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from tandau_app.manager import *

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Телефон нөмірі форматта енгізілуі керек:'+7(***)-***-**-**'.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True)
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    state = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    school = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

 

class University(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    description = models.TextField()



class Question(models.Model):
    question_text_ru = models.TextField() # Russian question text
    question_text_kz = models.TextField()  # Kazakh question text
    person_type = models.CharField(max_length=50)  # Assuming the type of person is a string field

