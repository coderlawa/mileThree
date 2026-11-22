from django.db import migrations
from django.utils.text import slugify


def populate_blank_slugs(apps, schema_editor):
    Recipe = apps.get_model('recipes', 'Recipe')
    database = schema_editor.connection.alias
    recipes = Recipe.objects.using(database).filter(slug='').order_by('pk')

    for recipe in recipes:
        base_slug = slugify(recipe.title) or f'recipe-{recipe.pk}'
        base_slug = base_slug[:254]
        slug = base_slug
        suffix = 2

        while Recipe.objects.using(database).filter(slug=slug).exclude(pk=recipe.pk).exists():
            suffix_text = f'-{suffix}'
            slug = f'{base_slug[:254 - len(suffix_text)]}{suffix_text}'
            suffix += 1

        Recipe.objects.using(database).filter(pk=recipe.pk).update(slug=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipe_is_public'),
    ]

    operations = [
        migrations.RunPython(populate_blank_slugs, migrations.RunPython.noop),
    ]
