from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe


class RecipeVisibilityTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='password')
        self.other_user = User.objects.create_user(username='other', password='password')
        self.recipe = Recipe.objects.create(
            title='Test recipe',
            slug='test-recipe',
            description='A test recipe',
            author=self.author,
            status=0,
        )

    def test_author_can_make_recipe_public(self):
        self.client.force_login(self.author)

        response = self.client.post(
            '/recipe_detail/test-recipe/',
            {'status': '1'},
        )

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.status, 1)
        self.assertRedirects(response, '/recipe_detail/test-recipe/')

    def test_author_can_make_recipe_private(self):
        self.recipe.status = 1
        self.recipe.save(update_fields=['status'])
        self.client.force_login(self.author)

        response = self.client.post('/recipe_detail/test-recipe/', {})

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.status, 0)
        self.assertRedirects(response, '/recipe_detail/test-recipe/')

    def test_non_author_cannot_change_recipe_visibility(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            '/recipe_detail/test-recipe/',
            {'status': '1'},
        )

        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.status, 0)
        self.assertRedirects(response, '/recipe_detail/test-recipe/')


class RecipeCreationTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='password')
        self.client.force_login(self.author)

    def test_add_recipe_generates_slug_from_title(self):
        response = self.client.post(
            reverse('add_recipe'),
            {'title': 'Fresh Air', 'description': 'A test recipe'},
        )

        recipe = Recipe.objects.get(title='Fresh Air')
        self.assertEqual(recipe.slug, 'fresh-air')
        self.assertRedirects(
            response,
            reverse('recipe_detail', kwargs={'slug': 'fresh-air'}),
        )

    def test_add_recipe_adds_suffix_for_duplicate_title(self):
        Recipe.objects.create(
            title='Fresh Air',
            slug='fresh-air',
            description='Existing recipe',
            author=self.author,
        )

        response = self.client.post(
            reverse('add_recipe'),
            {'title': 'Fresh Air', 'description': 'Another test recipe'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Recipe.objects.filter(slug='fresh-air-2').exists())
