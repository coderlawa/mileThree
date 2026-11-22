from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from allauth.account.models import EmailAddress
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


class ProfileSettingsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile-user',
            password='Original-Password-927!',
            email='profile@example.com',
        )
        self.client.force_login(self.user)

    def test_settings_page_renders_account_and_delete_fields(self):
        response = self.client.get(reverse('profile-settings'))

        self.assertEqual(response.status_code, 200)
        for field_name in (
            'username',
            'email',
            'new_password',
            'confirm_new_password',
            'current_password',
            'confirm_delete',
        ):
            self.assertContains(response, f'name="{field_name}"')
        self.assertContains(response, 'Update information')
        self.assertContains(response, 'Delete account')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_change_waits_for_verification_and_blank_password_is_unchanged(self):
        response = self.client.post(
            reverse('profile-settings'),
            {
                'username': 'updated-user',
                'email': 'updated@example.com',
                'new_password': '',
                'confirm_new_password': '',
            },
        )

        self.user.refresh_from_db()
        pending_email = EmailAddress.objects.get_new(self.user)

        self.assertRedirects(response, reverse('profile-settings'))
        self.assertEqual(self.user.username, 'updated-user')
        self.assertEqual(self.user.email, 'profile@example.com')
        self.assertTrue(self.user.check_password('Original-Password-927!'))
        self.assertEqual(pending_email.email, 'updated@example.com')
        self.assertFalse(pending_email.verified)
        self.assertEqual(len(mail.outbox), 1)

    def test_new_password_is_updated_and_session_remains_authenticated(self):
        response = self.client.post(
            reverse('profile-settings'),
            {
                'username': self.user.username,
                'email': self.user.email,
                'new_password': 'A-Very-Different-Password-827!',
                'confirm_new_password': 'A-Very-Different-Password-827!',
            },
        )

        self.user.refresh_from_db()
        self.assertRedirects(response, reverse('profile-settings'))
        self.assertTrue(self.user.check_password('A-Very-Different-Password-827!'))
        self.assertEqual(self.client.get(reverse('profile-settings')).status_code, 200)

    def test_account_deletion_requires_correct_password_and_confirmation(self):
        recipe = Recipe.objects.create(
            title='Owned recipe',
            slug='owned-recipe',
            description='Will be removed with the account',
            author=self.user,
        )

        response = self.client.post(
            reverse('profile-settings'),
            {
                'delete_account': '1',
                'current_password': 'wrong-password',
                'confirm_delete': 'on',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertTrue(Recipe.objects.filter(pk=recipe.pk).exists())

        response = self.client.post(
            reverse('profile-settings'),
            {
                'delete_account': '1',
                'current_password': 'Original-Password-927!',
                'confirm_delete': 'on',
            },
        )

        self.assertRedirects(response, reverse('home'))
        self.assertFalse(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())
