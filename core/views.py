from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from core.forms import SearchForm

def index_page(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['input']
            print(text)
        else:
            print('LOLLLLLOLOLOL')
    context = dict()
    return render(request, 'index.html', context)


def is_auth(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')
    else:
        return HttpResponseRedirect('/login_to_account')


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html')
    else:
        return HttpResponseRedirect('/login_to_account')

def login_to(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')
    else:
        return render(request, 'login_to_account.html')

def cart(request):
    return render(request, 'cart.html')