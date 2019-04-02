from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import include

from core.forms import SignUpForm


def index_page(request):
    context = dict()
    context['image'] = open('media/images/logo.png')
    return render(request, 'index.html', context)

#Authentication

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
#
