from django.shortcuts import redirect, render


def index_page(request):
    context = dict()
    context['image'] = open('media/images/logo.png')
    return render(request, 'index.html', context)
