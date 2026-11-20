from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_recipes, name='recipes'),
    path('<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('edit/<slug:slug>/', views.edit_recipe, name='edit_recipe')
]