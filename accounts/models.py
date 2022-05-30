from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
