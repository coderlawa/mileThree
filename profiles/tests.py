from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe


class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile-user',
            password='password',
            email='profile@example.com',
        )
        self.client.force_login(self.user)

    def test_profile_page_shows_vertical_navigation(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profile-nav')
        self.assertContains(response, reverse('profile-settings'))
        self.assertContains(response, reverse('home'))

    def test_profile_page_shows_all_of_the_users_recipes(self):
        private_recipe = Recipe.objects.create(
            title='Private Recipe',
            slug='private-recipe',
            description='Not public',
            author=self.user,
            status=0,
            is_public=False,
        )
        other_user = get_user_model().objects.create_user(
            username='another-user',
            password='password',
        )
        Recipe.objects.create(
            title='Another User Recipe',
            slug='another-user-recipe',
            description='Not owned by the profile user',
            author=other_user,
            status=1,
        )

        response = self.client.get(reverse('profile'))

        self.assertContains(response, private_recipe.title)
        self.assertContains(response, 'Private')
        self.assertNotContains(response, 'Another User Recipe')
