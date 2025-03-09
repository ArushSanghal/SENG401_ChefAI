from django.urls import path
from .views import register_user, login_user, get_user_data

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('user/', get_user_data, name='user-data'),
]
