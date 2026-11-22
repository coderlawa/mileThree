from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile(request):
    return render(
        request,
        'profiles/profile.html',
        {'profile_user': request.user},
    )


@login_required
def profile_settings(request):
    return render(
        request,
        'profiles/profile-settings.html',
        {'profile_user': request.user},
    )
