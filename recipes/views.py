from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q

from recipes.models import Recipe

# Create your views here.

def all_recipes(request):
    """
    A view to return all the searched recipes.
    """
    recipes = Recipe.objects.filter(is_public=True, status=1)
    query = None

    if 'q' in request.GET:
            query = request.GET['q'].strip()
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('recipes'))

            queries = Q(title__icontains=query) | Q(description__icontains=query)
            recipes = recipes.filter(queries)

    context = {
        'recipes': recipes,
        'search_term': query
    }
    
    return render(request, 'recipes/recipes.html', context)

def recipe_detail(request, slug):
    """
    A view to return the recipe detail page for a specific recipe based on its slug.
    """
    # Fetch the recipe based on the provided slug
    queryset = Recipe.objects.all()  # Fetch all recipes, including private ones
    recipe = get_object_or_404(queryset, slug=slug)

    if request.method == 'POST':
        if request.user != recipe.author:
            messages.error(request, "You are not authorized to change this recipe.")
            return redirect('recipe_detail', slug=slug)

        status = request.POST.get('status')
        if status not in (None, '1'):
            messages.error(request, "Invalid recipe status.")
            return redirect('recipe_detail', slug=slug)

        recipe.status = 1 if status == '1' else 0
        recipe.save(update_fields=['status'])
        messages.success(request, "Recipe visibility updated.")
        return redirect('recipe_detail', slug=slug)
    
    context = {
        'recipe': recipe
    }
    
    return render(request, 'recipes/recipe-detail.html', context)

def edit_recipe(request, slug):
    """
    A view to handle the editing of a recipe.
    """
    recipe = get_object_or_404(Recipe, slug=slug)

    # Check if the user is the author of the recipe
    if request.user != recipe.author:
        messages.error(request, "You are not authorized to edit this recipe.")
        return redirect('recipe_detail', slug=slug)

    # Handle form submission for editing the recipe (not implemented here)
    # You would typically use a form to handle the editing process

    context = {
        'recipe': recipe
    }
    
    return render(request, 'recipes/edit-recipe.html', context)