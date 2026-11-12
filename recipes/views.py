from django.shortcuts import render

from recipes.models import Recipe

# Create your views here.
def recipe_detail(request, slug):
    """
    A view to return the recipe detail page for a specific recipe based on its slug.
    """
    # Fetch the recipe based on the provided slug
    recipe = Recipe.objects.get(slug=slug)
    
    context = {
        'recipe': recipe
    }
    
    return render(request, 'recipes/recipe_detail.html', context)