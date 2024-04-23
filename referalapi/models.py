from decouple import config
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import MinLengthValidator
from django.db import models

from .managers import UserManager


# Create your models here.
class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=11,
                                    validators=[MinLengthValidator(11)],
                                    unique=True)
    my_invite_code = models.CharField(max_length=config('INVITE_CODE_LENGTH', cast=int, default=6),
                                      validators=[
                                          MinLengthValidator(config('INVITE_CODE_LENGTH', cast=int, default=6))],
                                      unique=True)
    other_user_invite_code = models.ForeignKey('self',
                                               to_field='my_invite_code',
                                               related_name='referrals',
                                               on_delete=models.SET_NULL,
                                               blank=True,
                                               null=True,
                                               default=None)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.phone_number}'
