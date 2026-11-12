from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.recipe_detail, name='recipe_detail')
]