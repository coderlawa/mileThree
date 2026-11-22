from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ProfilePageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile-user',
            password='password',
            email='profile@example.com',
        )
        self.client.force_login(self.user)

    def test_profile_page_shows_vertical_navigation_and_user_details(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profile-nav')
        self.assertContains(response, reverse('profile-settings'))
        self.assertContains(response, reverse('recipes'))
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)
