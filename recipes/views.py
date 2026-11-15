from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from recipes.models import Recipe

# Create your views here.

def recipe_detail(request, slug):
    """
    A view to return the recipe detail page for a specific recipe based on its slug.
    """
    # Fetch the recipe based on the provided slug
    queryset = Recipe.objects.filter(status=1)  # Only fetch public recipes
    recipe = get_object_or_404(queryset, slug=slug)
    
    context = {
        'recipe': recipe
    }
    
    return render(request, 'recipes/recipe-detail.html', context)