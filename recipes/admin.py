from django.contrib import admin
from .models import Recipe
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.

@admin.register(Recipe)
class RecipeAdmin(SummernoteModelAdmin):
    list_display = ('title', 'author', 'is_public', 'created_on', 'updated_on')
    list_filter = ('is_public', 'created_on', 'updated_on')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_on',)
    summernote_fields = ('description',)  # Use Summernote for the description field

