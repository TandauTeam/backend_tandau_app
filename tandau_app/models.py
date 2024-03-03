from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from tandau_app.manager import *

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True)
    image = models.ImageField(upload_to='user_images', null=True, blank=True)

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

