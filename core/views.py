from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from core.models import Product, Category, Cart, OrderProduct, Order,\
    Addresses, Product, Question, StockProduct, Modification
from django.core.exceptions import ObjectDoesNotExist
from core.classes import OrderProductInformation
from django.contrib.auth.decorators import login_required
from ast import literal_eval
from json import dumps


def index_page(request):
    context = dict()
    return_categories(context)
    return render(request, 'index.html', context)


def is_auth(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')
    else:
        return HttpResponseRedirect('/login_to_account')


def login_to(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')
    else:
        return render(request, 'login_to_account.html')


"""
Если пользователь авторизован, в контексте лежат записи OrderProduct из базы данных.
Если пользователь не авторизован, в контексте лежат OrderProductInformation
"""


def cart_page(request):
    context = dict()
    if request.user.is_authenticated:
        user = request.user
        context['cart'] = user.cart.products.all()
    else:
        context['cart'] = request.session['cart']
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
        name = products[i].name.lower()
        new_text = text.lower()
        if name.find(new_text) != -1:
            search_result.append(products[i])
    return search_result


def return_categories(context):  # #May need refactoring: context passed by value and not by pointer
    context['cat'] = Category.objects.all()


def add_category(name):  # #Returns True if adding was successful
    if not Category.objects.get(name=str(name)).exists():
        new_cat = Category(name=str(name))
        new_cat.save()
        return True
    return False


def delete_category(name):  # #Returns True if removal was successful
    try:
        cat = Category.objects.get(name=str(name))
        cat.delete()
        return True
    except ObjectDoesNotExist:
        return False


def categories(request):  # #Передаем сюда айди категории
    context = dict()
    if request.method == 'GET':
        context['cat'] = request.GET.get('cat')
        if context['cat'] is not None:
            context['products'] = context['cat'].products.all()
        else:
            context['products'] = []
        if len(context['products']) == 0:
            context['none'] = True
        else:
            context['none'] = False
        return render(request, 'search.html', context)
    return render(request, 'search.html', context)


def find_modification(product, modification_dict):
    modifications = Modification.objects.get(product=product)
    for modification in modifications:
        current_modification_dict = literal_eval(modification.characteristics)
        if current_modification_dict == modification_dict:
            return modification
    return None


def find_stock_product(product, modification_dict):
    modification = find_modification(product, modification_dict)
    stock_product = StockProduct.get(product=product, modification=modification)
    return stock_product


def get_product_modification_parameters(product):
    sample_modification = product.modification.all()[0]
    sample_characteristics = sample_modification.characteristics
    sample_char_dict = literal_eval(sample_characteristics)
    parameters_list = list()
    for key, value in sample_char_dict.items():
        parameters_list.append(key)
    return parameters_list


def __add_to_cart_authenticated__(user, quantity, stock_product):
    try:
        current_cart = user.cart
    except ObjectDoesNotExist:
        current_cart = Cart(user=user)
        current_cart.save()

    order_product = OrderProduct()
    order_product.quantity = quantity
    order_product.stock_product = stock_product
    order_product.cart = current_cart
    order_product.save()


def __add_to_cart_unauthenticated__(quantity, stock_product, cart):
    order_product_info = OrderProductInformation(quantity=quantity, stock_product=stock_product)
    cart.append(order_product_info)


"""
В запросе через скрытое поле должне передаваться id продукта

Необходимо добавить:
1) Проверку на то, что в корзине уже не лежит такой StockProduct. Если лежит, то добавить новый заказ к старому.
2) Проверить, есть ли на складе (StockProduct.quantity) нужное количество вещей.
"""


def add_to_cart(request):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        parameters_list = get_product_modification_parameters(product)  # #Список параметров модификаций продукта
        modification_dict = dict()  # #Словарь модификаций конкретного экземпляра
        for parameter in parameters_list:
            if parameter in request.POST:
                modification_dict[parameter] = request.POST.get(parameter)
            else:
                raise NotImplementedError
        stock_product = find_stock_product(product, modification_dict)
        if request.user.is_authenticated:
            user = request.user
            __add_to_cart_authenticated__(user, quantity, stock_product)
        else:
            if 'cart' not in request.session:
                request.session['cart'] = []
            __add_to_cart_unauthenticated__(quantity, stock_product, request.session['cart'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  # #Возврат на урл, где юзер был до этого
    return redirect('/')


"""
В этот метод необходимо передать id соответствующего StockProduct
"""


def delete_from_cart(request):
    if request.method == 'POST':
        stock_product_id = request.POST.get('stock_product_id')
        stock_product = StockProduct.objects.get(id=stock_product_id)
        if request.user.is_authenticated:
            user = request.user
            order_product = user.cart.products.get(stock_product=stock_product)
            order_product.delete()
        else:
            for order_product_info in request.session['cart']:
                if order_product_info.stock_product == stock_product:
                    request.session['cart'].remove(order_product_info)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('/')


"""
Этот метод необходим для того, чтобы перенести корзину из кукей в базу данных
"""


def __cart_from_session_to_db__(current_cart, user):
    for information in current_cart:
        quantity = information.quantity
        stock_product = information.stock_product
        __add_to_cart_authenticated__(user, quantity, stock_product)


"""
В этот метод необходимо передать, какой адрес выбрал пользователь. Если пользователь зарегистрирован,
передается id адреса; в противном случае передается сам адрес (в виде строки?).
Если пользователь не авторизован, то прежде чем отправлять на этот метод, надо чтобы он
указал свою электронную почту для связи (вероятно, это придется делать на отдельной странице).
Также стоит добавить в этом методе оповещение пользователя об успешном заказе по электронной почте.
Необходимо добавить уменьшение числа вещей на складе после заказа.
"""


def make_order(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            order_products = user.cart.products.all()
            if len(order_products) == 0:
                raise NotImplementedError
            address_id = request.POST.get('address_id')
            address = Addresses.objects.get(id=address_id)
            order = Order(author=user,
                          address=address)
            for order_product in order_products:
                order_product.order = order
                order_product.save()
            order.save()
            return redirect('/profile')
        else:
            if 'cart' not in request.session or len(request.session['cart']) == 0:
                raise NotImplementedError
            address = request.POST.get('address')
            email = request.POST.get('email')
            current_cart = request.session['cart']
            order = Order(email=email, address=address)
            if address is None or email is None:
                raise ValueError
            for order_product_information in current_cart:
                order_product = OrderProduct(quantity=order_product_information.quantity,
                                             stock_product=order_product_information.stock_product,
                                             order=order)
                order_product.save()
            order.save()
            return redirect('/')
    return redirect('/')


def profile_info(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html')
    else:
        return HttpResponseRedirect('/login_to_account')


@login_required
def add_address(request):
    if request.method == 'POST':
        user = request.user
        city = request.POST.get('city')
        street = request.POST.get('street')
        building = request.POST.get('building')
        flat = request.POST.get('flat')
        entrance = request.POST.get('entrance')
        if Addresses.objects.filter(city=city, street=street, building=building, flat=flat, entrance=entrance).exists():
            ad = Addresses.objects.get(city=city, street=street, building=building, flat=flat, entrance=entrance)
            ad.customers.add(user)
        else:
            new_ad = Addresses(city=city,
                               street=street,
                               building=building,
                               flat=flat,
                               entrance=entrance)
            new_ad.save()
            new_ad.customers.add(user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('/')


'''
В этот метод необходимо передать id адреса, подлежащего удалению
'''


@login_required
def delete_address(request):
    user = request.user
    if request.method == 'POST':
        address_id = request.POST.get('id')
        address = Addresses.objects.get(id=address_id)
        user.addresses_set.remove(address)
    else:
        return redirect('/')


@login_required
def profile_addresses(request):
    user = request.user
    addresses = user.addresses_set.all()  # # Have some doubts about this line
    context = dict()
    context['addresses'] = addresses
    return render(request, 'addresses.html')


@login_required
def make_question(request):
    if request.method == 'POST':
        author = request.user
        topic = request.POST.get('topic')
        content = request.POST.get('content')
        question = Question(author=author, topic=topic, content=content)
        question.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('/')


@login_required
def view_questions_user(request):  # #Впоследствии надо сделать отдельное отображение отвеченных и неотвеченных вопросов
    context = dict()
    user = request.user
    context['questions'] = user.questions.all()
    return render(request, 'questions.html', context)


@login_required
def view_questions_admin(request):
    user = request.user
    if user.is_staff:
        context = dict()
        context['questions'] = Question.objects.filter(status='Рассматривается')
        return render(request, 'admin_view_questions.html', context)
    return redirect('/')
