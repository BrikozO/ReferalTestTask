from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from .views import UsersListView, UserProfileView, UserCreateView, EnterCodeView

urlpatterns = [
    path('', UsersListView.as_view(), name='all_users'),
    path('profile/<slug:phone_number>/', UserProfileView.as_view(), name='profile'),
    path('signin/', UserCreateView.as_view(), name='create_user'),
    path('entercode/', EnterCodeView.as_view(), name='enter_registration_code'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
