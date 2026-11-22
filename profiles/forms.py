from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()


class AccountSettingsForm(forms.ModelForm):
    new_password = forms.CharField(
        label='New password',
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text='Leave both password fields blank to keep your current password.',
    )
    confirm_new_password = forms.CharField(
        label='Confirm new password',
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = self.instance.email
        self.fields['email'].required = True
        self.order_fields(
            ['username', 'email', 'new_password', 'confirm_new_password']
        )

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password != confirm_new_password:
            self.add_error(
                'confirm_new_password',
                'The new password fields must match.',
            )
        elif new_password:
            try:
                validate_password(new_password, self.instance)
            except ValidationError as error:
                self.add_error('new_password', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.original_email

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()

        return user


class DeleteAccountForm(forms.Form):
    current_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )
    confirm_delete = forms.BooleanField(
        label='I understand that my account and recipes will be permanently deleted.',
    )

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data['current_password']
        if not self.user.check_password(current_password):
            raise ValidationError('Your current password is incorrect.')
        return current_password
