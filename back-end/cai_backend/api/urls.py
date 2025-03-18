from django.urls import path
from api.views import generate_recipe

urlpatterns = [
    path("generate_recipe/", generate_recipe, name="generate_recipe"),
]
