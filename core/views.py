from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from core.models import Product, Category, Cart, OrderProduct
from django.core.exceptions import ObjectDoesNotExist
from core.classes import OrderProductInformation


def index_page(request):
    context = dict()
    add_category("OLL")
    add_category("ekk")
    return_categories(context)
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
            context['products'] = search_in_base(context['text'])
        else:
            context['products'] = []
        if len(context['products']) == 0:
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


def return_categories(context):
    context['cat'] = Category.objects.all()


def add_category(name):  # #Returns True if adding was successful
    try:
        cat = Category.objects.get(name=str(name))
        return False
    except ObjectDoesNotExist:
        new_cat = Category(name = str(name))
        new_cat.save()
        return True


def delete_category(name):  # #Returns True if removal was successful
    try:
        cat = Category.objects.get(name=str(name))
        cat.delete()
        return True
    except ObjectDoesNotExist:
        return False


def categories(request):
    context = dict()
    if request.method == 'GET':
        context['cat'] = request.GET.get('cat')
        if context['cat'] is not None:
            context['products'] = Category.products.all()
        else:
            context['products'] = []
        if len(context['products']) == 0:
            context['none'] = True
        else:
            context['none'] = False
        return render(request, 'search.html', context)
    return render(request, 'search.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            try:
                current_cart = user.cart
            except ObjectDoesNotExist:
                current_cart = Cart(user=user)
                current_cart.save()

            order_product = OrderProduct()
            order_product.size = request.POST.get('size')
            order_product.quantity = request.POST.get('quantity')
            order_product.product = Product.objects.get(id=request.POST.get('product_id'))
            # #Необходимо, чтобы в запросе передавался айди продукта через скрытое поле
            order_product.cart = current_cart
            order_product.save()
        else:
            if 'cart' not in request.session:
                request.session['cart'] = []
            size = request.POST.get('size')
            quantity = request.POST.get('quantity')
            product_id = request.POST.get('product_id')
            order_product = OrderProductInformation(size=size, quantity=quantity, product_id=product_id)
            request.session['cart'].append(order_product)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  # #Возврат на урл, где юзер был до этого
    return redirect('/')

    # #Дописать формирование заказа


def delete_from_cart(request):  # #Необходимо передать айди OrderProduct или индекс в массиве
    if request.method == 'POST':
        if request.user.is_authenticated:
            order_product_id = request.POST.get('order_product_id')
            OrderProduct.objects.filter(id=order_product_id).delete()
        else:
            del(request.session['cart'][request.POST.get('order_product_id')])



