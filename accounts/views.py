from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

def register_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user_obj = form.save()
        messages.success(request, f"New user created successfully! Please log in.")
        return redirect('login')
    context = {"form": form}
    return render(request, "accounts/register.html", context)

def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('tracker:task_list')
        else:
            messages.error(request, "Incorrect username or password. Try again.")
    else:
        form = AuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)


@login_required
def private_access(request, reverse_url):
    user_profile  = getattr(request.user, "userprofile", None)

    if user_profile is None or not user_profile.special_privilege_password:
        messages.error(request, "You don't have a privilege to access private tasks.")
        return redirect(reverse_url)

    if request.method == "POST":
        pwd = request.POST.get("password")

        if pwd == user_profile.special_privilege_password:
            request.session['private_access'] = True
            messages.success(request, "Private mode unlocked successfully!")
            url = reverse(reverse_url) + "?view=private"
            return redirect(url)
        else:
            messages.error(request, "Incorrect password. Try again.")

    return render(request, "accounts/private_access.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully!")
        return redirect('login')
    return render(request, "accounts/logout.html", {})