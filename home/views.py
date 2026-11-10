from django.shortcuts import render
from recipes.models import Recipe

# Create your views here.

def index(request):
    """
    A view to return the index page returns all recipes - including search functionality and display by public/private status
    """

    recipes = Recipe.objects.all()
    context = {
        'recipes': recipes
    }
    
    return render(request, 'home/index.html', context)