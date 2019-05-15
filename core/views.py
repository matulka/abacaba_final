from django.shortcuts import redirect, render, render_to_response
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from core.models import Product, Category, Cart, OrderProduct, Order,\
    Addresses, Product, Question, StockProduct, Modification, OrderProductInformation
from django.core.exceptions import ObjectDoesNotExist
from ast import literal_eval
from json import dumps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from core.forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.hashers import check_password
from django.template.loader import render_to_string
from core.token import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.forms.models import model_to_dict
from django.core import serializers
from core.forms import AddressForm, ProfileForm, PasswordProfileForm
from django.template import RequestContext

def index_page(request):
    context = dict()
    context['cat'] = 'lol'
    context['products'] = return_products()
    return render(request, 'index.html', context)


def e_handler500(request):
    context = RequestContext(request)
    response = render_to_response('error500html', context)
    response.status_code = 500
    return response

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
        if 'cart' not in request.session:
            request.session['cart'] = list()
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
        return render(request, 'search.html', context)
    return render(request, 'search.html', context)


def search_in_base(text):
    products = Product.objects.all()
    search_result = []
    for i in range(len(products)):
        name = str(products[i].name).lower()
        new_text = str(text).lower()
        if name.find(new_text) != -1:
            search_result.append(products[i])
    return search_result


def return_categories():  # #May need refactoring: context passed by value and not by pointer
    return Category.objects.all()


def return_categories_http(request):
    string = str()
    for category in Category.objects.all():
        string = string + (str(category.id) + ',' + category.name + ',')
        if category.parent_category:
            string = string + (str(category.parent_category.id) + ';')
        else:
            string = string + 'None;'
    string = string[:(len(string) - 1)]
    d = dict()
    d['1'] = string
    return JsonResponse(d)


def return_products():
    return Product.objects.all()


def categories(request):  # #Передаем сюда айди категории
    context = dict()
    if request.method == 'GET':
        context['cat'] = request.GET.get('cat')
        try:
            cat = Category.objects.get(name=context['cat'])
            context['products'] = cat.products.all()
        except ObjectDoesNotExist:
            context['products'] = []
        return render(request, 'search.html', context)
    return render(request, 'search.html', context)


def find_modification(product, modification_dict):
    modifications = Modification.objects.filter(product=product)
    for modification in modifications:
        current_modification_dict = literal_eval(modification.characteristics)
        if current_modification_dict == modification_dict:
            return modification
    return None


def find_stock_product(product, modification_dict):
    modification = find_modification(product, modification_dict)
    stock_product = StockProduct.objects.get(product=product, modification=modification)
    return stock_product


def get_product_modification_parameters(product):
    sample_modification = product.modifications.all()[0]
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
        current_cart = Cart(author=user)
        current_cart.save()
    if OrderProduct.objects.filter(cart=current_cart, stock_product=stock_product).exists():
        prod = OrderProduct.objects.get(cart=current_cart, stock_product=stock_product)
        if int(quantity) + prod.quantity > stock_product.quantity:
            raise ValueError
        else:
            prod.quantity += int(quantity)
            prod.save()
    else:
        if int(quantity) > stock_product.quantity:
            raise ValueError
        else:
            order_product = OrderProduct()
            order_product.quantity = int(quantity)
            order_product.stock_product = stock_product
            order_product.cart = current_cart
            order_product.save()


def __add_to_cart_unauthenticated__(quantity, stock_product, cart):
    order_product_info = OrderProductInformation(quantity=quantity, stock_product=stock_product)
    cart.append(model_to_dict(order_product_info))


"""
В запросе через скрытое поле должне передаваться id продукта

Необходимо добавить:
1) Проверку на то, что в корзине уже не лежит такой StockProduct. Если лежит, то добавить новый заказ к старому.
2) Проверить, есть ли на складе (StockProduct.quantity) нужное количество вещей.
"""


def add_to_cart(request):
    context = dict()
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
        context['d'] = modification_dict
        stock_product = find_stock_product(product, modification_dict)
        if request.user.is_authenticated:
            user = request.user
            try:
                __add_to_cart_authenticated__(user, quantity, stock_product)
            except ValueError:
                e_handler500(request)
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
        try:
            stock_product = StockProduct.objects.get(id=stock_product_id)
            if request.user.is_authenticated:
                user = request.user
                order_product = user.cart.products.get(stock_product=stock_product)
                order_product.delete()
            else:
                for order_product_info in request.session['cart']:
                    if StockProduct.objects.get(id=order_product_info['stock_product']) == stock_product:
                        request.session['cart'].remove(order_product_info)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except ObjectDoesNotExist:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('/')


"""
Этот метод необходим для того, чтобы перенести корзину из кукей в базу данных
"""


def __cart_from_session_to_db__(current_cart, user):
    for information in current_cart:
        quantity = information['quantity']
        stock_product = StockProduct.objects.get(id=information['stock_product'])
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


@login_required
def profile_info(request):
    return render(request, 'profile.html')


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            city = form.cleaned_data['city']
            street = form.cleaned_data['street']
            building = form.cleaned_data['building']
            flat = form.cleaned_data['flat']
            entrance = form.cleaned_data['entrance']
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
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('/')


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


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Вы успешно подтвердили e-mail и вошли в свой аккаунт!')
        return redirect('home')
    else:
        messages.error(request, 'Ссылка для регистрации устарела')
        return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Активируйте ваш аккаунт'
            message = render_to_string('registration/account_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, 'На ваш адрес ' + to_email + ' выслано письмо для завершения регистрации')
            return redirect('home')
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):

    if request.method == 'POST':
        if "first_name" in request.POST:
            form_name = ProfileForm(request.POST)
            user = User.objects.get(username=request.user.username)
            user.first_name = form_name['first_name'].data
            user.last_name = form_name['last_name'].data
            user.save()
            messages.success(request, 'Вы успешно изменили свои данные')
        else:
            form_password = PasswordProfileForm(request.POST)
            password1 = form_password['password1'].data
            password2 = form_password['password2'].data
            user = User.objects.get(username=request.user.username)

            if not user.check_password(password1):
                messages.error(request, 'Вы ввели неверный пароль', extra_tags='danger')

            else:
                user.set_password(password2)
                user.save()
                login(request, user)
                messages.success(request, 'Вы успешно изменили пароль')

        return redirect('profile')

    else:
        form_password = PasswordProfileForm()
        form_name = ProfileForm()
        form_name.fields["first_name"].initial = request.user.first_name
        form_name.fields["last_name"].initial = request.user.last_name

    return render(request, 'registration/profile.html', {'form_name':form_name, 'form_password':form_password})


@login_required
def profile_orders(request):
    user = User.objects.get(username=request.user.username)
    orders = OrderProduct.objects.all().filter(order__author=user)

    if orders.count() == 0:
        return render(request, 'registration/profile_orders.html', {'empty': 'yes'})

    return render(request, 'registration/profile_orders.html', {'orders': orders})


@login_required
def profile_addresses(request):
    user = User.objects.get(username=request.user.username)
    addresses = user.addresses.all().filter(customer=user)

    if addresses.count() == 0:
        return render(request, 'registration/addresses.html', {'empty': 'yes'})

    if request.method == 'GET':
        if request.GET.get('id'):
            form_address = AddressForm()
            data = request.GET.dict()
            id_ = int(data['id']) - 1
            address = addresses[id_]
            return render(request,  'registration/addresses.html',
                          {'addresses': addresses, 'form_address': form_address, 'address': address, 'id': id_})

    if request.method == 'POST':
        form_address = AddressForm(request.POST)

        id_address = form_address.data.get('id')
        city = form_address.data.get('city')
        street = form_address.data.get('street')
        building = form_address.data.get('building')
        entrance = form_address.data.get('entrance')
        flat = form_address.data.get('flat')
        description = form_address.data.get('description')

        if form_address.is_valid():

            if id_address is not None:
                address = addresses[int(id_address)]

                address.city = city
                address.street = street
                address.building = building
                address.entrance = entrance
                address.flat = flat
                address.description = description

                address.save()

    return render(request, 'registration/addresses.html', {'addresses': addresses})


@login_required
def profile_issues(request):
    user = User.objects.get(username=request.user.username)
    issues = user.questions.all().filter(author=user)

    if issues.count() == 0:
        return render(request, 'registration/issues.html', {'empty': 'yes'})

    if request.method == 'GET':
        if request.GET.get('issue'):
            data = request.GET.dict()
            issue = issues[int(data['issue'])-1]
            return render(request, 'registration/issue.html', {'issue': issue})

    return render(request, 'registration/issues.html', {'issues': issues})
