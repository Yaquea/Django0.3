from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm

def main(request):
    return render(request, 'main.html', {

    })

def signup(request):
    if request.method == ('GET'):
         return render(request, 'signup.html', { 'form':SignupForm() ,

         })
    else:
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.password = make_password(form.cleaned_data['password1'])  # Hash password
            user.save()  # Now save to DB
            return redirect('login')  # Redirect to login page or another view
        
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm()})
    else:
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('main')
        else:
            # Extract error message from form or use a default
            error = "Invalid username or password. Please try again."
            return render(request, 'login.html', {'form': form, 'error': error})
