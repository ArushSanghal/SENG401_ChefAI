from django.urls import path
from api.views import generate_recipe

urlpatterns = [
    path("generate-recipe/", generate_recipe),
]
