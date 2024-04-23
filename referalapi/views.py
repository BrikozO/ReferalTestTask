import random
import time
from string import ascii_letters, digits

from decouple import config
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response

from .models import User
from .serializers import UserProfileSerializer, UserCreationSerializer, EnterCodeSerializer
from .constants import SUCCESS_USER_CREATION, GET_VERIFICATION_CODE_MESSAGE, SUCCESS_USER_LOGIN, \
    GET_VERIFICATION_CODE_API_MESSAGE
from .rediscli import redis_client
from .permissions import IsAuthorOrReadOnly


# Create your views here.
class UsersListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'phone_number'
    lookup_url_kwarg = 'phone_number'


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Imitation of server working
        time.sleep(1)
        code: str = ''.join(
            random.choice(ascii_letters + digits) for _ in range(config('VERIFICATION_CODE_LEN', cast=int, default=4)))
        print(GET_VERIFICATION_CODE_MESSAGE.format(code=code))
        redis_client.set(code, request.data['phone_number'])
        redis_client.expire(code, 60)
        uri: str = reverse('enter_registration_code')
        return Response({'message': GET_VERIFICATION_CODE_API_MESSAGE, 'code-enter-endpoint': uri, 'code': code},
                        status=status.HTTP_202_ACCEPTED)


class EnterCodeView(CreateAPIView):
    serializer_class = EnterCodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number: str = redis_client.get(request.data['code']).decode('utf-8')
        redis_client.delete(request.data['code'])
        user = User.objects.filter(phone_number=phone_number)
        if not user.exists():
            user = User.objects.create_user(phone_number=phone_number)
            Token.objects.create(user=user)
            return Response(SUCCESS_USER_CREATION.format(phone=phone_number), status=status.HTTP_201_CREATED)
        token = Token.objects.get(user=user.first())
        login(request, user=user.first())
        return Response({f'{SUCCESS_USER_LOGIN}': token.key}, status=status.HTTP_200_OK)
