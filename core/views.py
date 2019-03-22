from django.shortcuts import redirect, render

def index_page(request):
    context = {}
    return render(request, 'index.html', context)
