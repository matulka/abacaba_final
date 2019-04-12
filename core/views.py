from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect, JsonResponse
from core.models import Product, Category, Cart, OrderProduct, Order, Addresses, Product, Question
from django.core.exceptions import ObjectDoesNotExist
from core.classes import OrderProductInformation
from django.contrib.auth.decorators import login_required


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
        new_cat = Category(name=str(name))
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


def __add_to_cart_authenticated__(user, size, quantity, product_id):
    try:
        current_cart = user.cart
    except ObjectDoesNotExist:
        current_cart = Cart(user=user)
        current_cart.save()

    order_product = OrderProduct()
    order_product.size = size
    order_product.quantity = quantity
    order_product.product = Product.objects.get(id=product_id)
    order_product.cart = current_cart
    order_product.save()


def __add_to_cart_unauthenticated__(size, quantity, product_id, cart):
    order_product = OrderProductInformation(size=size, quantity=quantity, product_id=product_id)
    cart.append(order_product)


"""
В запросе через скрытое поле должне передаваться id продукта
"""


def add_to_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            size = request.POST.get('size')
            quantity = request.POST.get('quantity')
            product_id = request.POST.get('product_id')
            __add_to_cart_authenticated__(user, size, quantity, product_id)
        else:
            if 'cart' not in request.session:
                request.session['cart'] = []
            size = request.POST.get('size')
            quantity = request.POST.get('quantity')
            product_id = request.POST.get('product_id')
            __add_to_cart_unauthenticated__(size, quantity, product_id, request.session['cart'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  # #Возврат на урл, где юзер был до этого
    return redirect('/')


"""
В этот метод необходимо передать id соответствующего OrderProduct или его индекс в массиве (для
незарегистрированных пользователей)
"""


def delete_from_cart(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            order_product_id = request.POST.get('order_product_id')
            OrderProduct.objects.filter(id=order_product_id).delete()
        else:
            del(request.session['cart'][request.POST.get('order_product_id')])


"""
Этот метод необходим для того, чтобы при входе в систему корзина пользователя, которая хранилась
в куки, сохранялась в базе данных
"""


def __cart_from_session_to_db__(current_cart, user):
    for information in current_cart:
        size = information.size
        quantity = information.quantity
        product_id = information.product_id
        __add_to_cart_authenticated__(user, size, quantity, product_id)


"""
В этот метод необходимо передать, какой адрес выбрал пользователь. Если пользователь зарегистрирован,
передается id адреса; в противном случае передается сам адрес (в виде строки?).
Если пользователь не авторизован, то прежде чем отправлять на этот метод, надо чтобы он
указал свою электронную почту для связи (вероятно, это придется делать на отдельной странице).
Также стоит добавить в этом методе оповещение пользователя об успешном заказе по электронной почте.
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
                order_product = OrderProduct(size=order_product_information.size,
                                             quantity=order_product_information.quantity,
                                             product=Product.objects.get(id=order_product_information.product_id))
                order_product.order = order
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
