from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def register_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user_obj = form.save()
        return redirect('login')
    context = {"form": form}
    return render(request, "accounts/register.html", context)

# Create your views here.
def login_view(request):
    # future -> ?next=/articles/create/
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tracker:task_list')
    else:
        form = AuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)


@login_required
def private_access(request):
    user_profile  = getattr(request.user, "userprofile", None)

    if user_profile is None or not user_profile.special_privilege_password:
        messages.error(request, "You don't have a privilege to access private tasks.")
        return redirect("tracker:task_list")

    if request.method == "POST":
        pwd = request.POST.get("password")

        if pwd == user_profile.special_privilege_password:
            request.session['private_access'] = True
            messages.success(request, "Private mode unlocked successfully!")
            url = reverse("tracker:task_list") + "?view=private"
            return redirect(url)
        else:
            messages.error(request, "Incorrect password. Try again.")

    return render(request, "accounts/private_access.html")

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')
    return render(request, "accounts/logout.html", {})