from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
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
            return redirect('main')  # Redirect to login page or another view