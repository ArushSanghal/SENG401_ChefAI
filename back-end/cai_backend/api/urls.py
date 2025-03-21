from django.urls import path
from api.views import generate_recipe, register_user, login_user, get_user_data, update_user_profile, logout_user, save_button, view_recipes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('user/', get_user_data, name='user-data'),
    path('update-user/', update_user_profile, name='update-user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_user, name='logout'),
    path('generate_recipe/', generate_recipe, name='generate_recipe'), # type: ignore
    path('save_button/', save_button, name='save_button'), # type: ignore
    path('view_recipes/', view_recipes, name='view_recipes') # type: ignore
]
