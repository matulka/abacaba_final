from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from core.forms import SearchForm
from core.models import Product


def index_page(request):
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


def search(request):
    context = dict()
    if request.method == 'GET':
        context['text'] = request.GET.get('text')
        print(context['text'])
        if context['text'] is not None:
            context['result'] = search_in_base(context['text'])
        else:
            context['result'] = []
        if len(context['result']) == 0:
            context['none'] = True
        else:
            context['none'] = False
        return render(request, 'search.html', context)
    return render(request, 'search.html', context)


def search_in_base(text):
    products = Product.objects.all()
    search_result = []
    for i in range(len(products)):
        name = products[i].name
        name.lower()
        new_text = text.lower()
        if name.find(new_text) != -1:
            search_result.append(products[i])
    return search_result



