from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils.text import slugify
from html import unescape

from urllib3 import request

from recipes.models import Recipe
from recipes.forms import RecipeForm

# Create your views here.

def all_recipes(request):
    """
    A view to return all the searched recipes.
    """

    recipes = Recipe.objects.filter(is_public=True, status=1)
    query = None

    # Fetch public recipes and private recipes of the logged-in user
    if request.user.is_authenticated:
        recipes = recipes | Recipe.objects.filter(author=request.user, status=0)
        
    

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

def add_recipe(request):
    """
    A view to handle the addition of a new recipe.
    """
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        if recipe_form.is_valid():
            new_recipe = recipe_form.save(commit=False)
            new_recipe.author = request.user
            base_slug = slugify(new_recipe.title) or 'recipe'
            new_recipe.slug = base_slug
            suffix = 2

            while Recipe.objects.filter(slug=new_recipe.slug).exists():
                new_recipe.slug = f'{base_slug}-{suffix}'
                suffix += 1

            new_recipe.save()
            messages.success(request, "Recipe added successfully.")
            return redirect('recipe_detail', slug=new_recipe.slug)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        recipe_form = RecipeForm()

    context = {
        'recipe_form': recipe_form
    }
    
    return render(request, 'recipes/add-recipe.html', context)

def edit_recipe(request, slug):
    """
    A view to handle the editing of a recipe.
    """
    recipe = get_object_or_404(Recipe, slug=slug)
    recipe_form = RecipeForm(
        instance=recipe,
        initial={'description': unescape(strip_tags(recipe.description))})

    # Check if the user is the author of the recipe
    if request.user != recipe.author:
        messages.error(request, "You are not authorized to edit this recipe.")
        return redirect('recipe_detail', slug=slug)

    # Handle form submission
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if recipe_form.is_valid():
            recipe_form.save()
            messages.success(request, "Recipe updated successfully.")
            return redirect('recipe_detail', slug=slug)
        else:
            messages.error(request, "Please correct the errors below.")
            
    context = {
        'recipe': recipe,
        'recipe_form': recipe_form
    }
    
    return render(request, 'recipes/edit-recipe.html', context)

def delete_recipe(request, slug):
    """
    A view to handle the deletion of a recipe.
    """
    recipe = get_object_or_404(Recipe, slug=slug)

    # Check if the user is the author of the recipe
    if request.user != recipe.author:
        messages.error(request, "You are not authorized to delete this recipe.")
        return redirect('recipe_detail', slug=slug)

    # Handle deletion confirmation
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recipe deleted successfully.")
        return redirect('home')