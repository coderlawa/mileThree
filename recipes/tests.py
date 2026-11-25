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


class RecipeAuthorBrowseTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='recipe-author', password='password')
        self.visitor = User.objects.create_user(username='visitor', password='password')
        self.public_recipe = Recipe.objects.create(
            title='Public recipe',
            slug='public-recipe',
            description='Public description',
            author=self.author,
            is_public=True,
            status=1,
        )
        Recipe.objects.create(
            title='Private recipe',
            slug='private-recipe',
            description='Private description',
            author=self.author,
            is_public=False,
            status=0,
        )
        Recipe.objects.create(
            title='Another author recipe',
            slug='another-author-recipe',
            description='Different author',
            author=self.visitor,
            is_public=True,
            status=1,
        )

    def test_owner_author_link_goes_to_own_profile(self):
        self.client.force_login(self.author)
        response = self.client.get(
            reverse('recipe_detail', kwargs={'slug': self.public_recipe.slug})
        )

        self.assertContains(response, f'href="{reverse("profile")}">recipe-author</a>')

    def test_other_viewer_author_link_filters_to_public_recipes_by_author(self):
        response = self.client.get(
            reverse('recipe_detail', kwargs={'slug': self.public_recipe.slug})
        )

        self.assertContains(
            response,
            f'href="{reverse("recipes")}?author=recipe-author">recipe-author</a>',
        )

        results = self.client.get(
            reverse('recipes'),
            {'author': self.author.username},
        )

        self.assertEqual(list(results.context['recipes']), [self.public_recipe])

    def test_author_filter_can_be_narrowed_by_existing_text_search(self):
        response = self.client.get(
            reverse('recipes'),
            {'author': self.author.username, 'q': 'Public'},
        )

        self.assertEqual(list(response.context['recipes']), [self.public_recipe])
