from allauth.account.forms import AddEmailForm
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from django.shortcuts import redirect, render

from profiles.forms import AccountSettingsForm, DeleteAccountForm


@login_required
def profile(request):
    return render(
        request,
        'profiles/profile.html',
        {
            'profile_user': request.user,
            'recipes': request.user.recipes.filter(is_public=True, status=1) | request.user.recipes.filter(status=0),
        },
    )


@login_required
def profile_settings(request):
    account_form = AccountSettingsForm(instance=request.user)
    delete_form = DeleteAccountForm(user=request.user)

    if request.method == 'POST' and 'delete_account' in request.POST:
        delete_form = DeleteAccountForm(request.POST, user=request.user)
        if delete_form.is_valid():
            user = request.user
            user.delete()
            logout(request)
            messages.success(
                request,
                'Your account and its recipes have been permanently deleted.',
            )
            return redirect('home')
    elif request.method == 'POST':
        account_form = AccountSettingsForm(
            request.POST,
            instance=request.user,
        )
        if account_form.is_valid():
            new_email = account_form.cleaned_data['email']
            email_changed = (
                new_email.casefold() != account_form.original_email.casefold()
            )
            email_form = None

            if email_changed:
                email_form = AddEmailForm(
                    user=request.user,
                    data={'email': new_email},
                )
                if not email_form.is_valid():
                    for error in email_form.errors.get('email', []):
                        account_form.add_error('email', error)

            if not account_form.errors:
                user = account_form.save()
                if account_form.cleaned_data['new_password']:
                    update_session_auth_hash(request, user)

                if email_form:
                    email_form.save(request)
                    messages.info(
                        request,
                        'Account updated. Verify your new email address to '
                        'complete the email change; your current email remains '
                        'active until then.',
                    )
                else:
                    messages.success(request, 'Account information updated.')
                return redirect('profile-settings')

    return render(
        request,
        'profiles/profile-settings.html',
        {
            'profile_user': request.user,
            'account_form': account_form,
            'delete_form': delete_form,
            'pending_email': EmailAddress.objects.get_new(request.user),
        },
    )
