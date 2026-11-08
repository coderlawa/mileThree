from django.contrib import admin
from .models import Recipe

# Register your models here.

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_public', 'created_on', 'updated_on')
    list_filter = ('is_public', 'created_on', 'updated_on')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_on',)

admin.site.register(Recipe, RecipeAdmin)