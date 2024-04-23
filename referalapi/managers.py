import random
from string import ascii_letters, digits

from decouple import config
from django.contrib.auth.base_user import BaseUserManager
from rest_framework.authtoken.models import Token

from .constants import PHONE_NUMBER_DONT_SET_ERROR, PHONE_NUMBER_IS_NOT_VALID


class UserManager(BaseUserManager):
    use_in_migrations = True

    @staticmethod
    def normalize_phone_number(phone_number: str):
        if not phone_number or len(phone_number) == 0:
            raise ValueError(PHONE_NUMBER_DONT_SET_ERROR)
        elif not phone_number.isdigit():
            raise ValueError(PHONE_NUMBER_IS_NOT_VALID)
        phone_number: str = phone_number.replace(' ', '').replace('+', '').replace('(', '').replace(')', '').replace(
            '-', '')
        if len(phone_number) == 10:
            phone_number = '7' + phone_number
        return phone_number

    def _create_user(self, phone_number, **extra_fields):
        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        symbs: str = ascii_letters + digits
        user.my_invite_code = ''.join(
            random.choice(symbs) for _ in range(config('INVITE_CODE_LENGTH', cast=int, default=6)))
        user.set_unusable_password()
        user.save()
        return user

    def create_user(self, phone_number, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, **extra_fields)

    def create_superuser(self, phone_number, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(phone_number, **extra_fields)
