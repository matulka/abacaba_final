from django.shortcuts import redirect, render, render_to_response
from django.views.decorators.csrf import csrf_exempt
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
from django.template.loader import render_to_string
from core.token import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.forms.models import model_to_dict
from django.core import serializers
from core.forms import AddressForm, QuestionForm
from django.template import RequestContext


def admin_page(request):
    if request.user.is_staff:
        return render(request, 'admin/admin_index.html')
    return redirect('/')

def arr_to_str(arr):
    string = str()
    for element in arr:
        string += str(element) + ','
    string = string[:(len(string) - 1)]
    return string


def index_page(request):
    context = dict()
    if request.method == 'GET' and 'category_id' in request.GET:
        context['products'] = return_products(request.GET.get('category_id'))
    else:
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
        if context['text'] is not None:
            context['products'] = search_in_base(context['text'])
        else:
            context['products'] = []
        return render(request, 'index.html', context)
    return render(request, 'index.html', context)


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


def return_categories_json(request):  # #Возвращает данные о категориях в виде JSON
    string = str()
    for category in Category.objects.all():
        string = string + (str(category.id) + ',' + category.name + ',')
        if category.parent_category:
            string = string + (str(category.parent_category.id) + ';')
        else:
            string = string + 'None;'
        print(string)
    string = string[:(len(string) - 1)]
    d = dict()
    d['1'] = string
    return JsonResponse(d)


def browse_product(request):  # #Возвращает контекст для отображения страницы товара
    context = dict()
    if request.method == 'GET':
        if 'id' in request.GET:
            product = Product.objects.get(id=request.GET['id'])
            context['product'] = product
            return render(request, 'product_page.html', context)
    return render(request, 'index.html', context)  # #In case there is no such product or request.method wasn't GET


def return_products(category_id=None):  # #Возвращает список продуктов для главной страницы
    if category_id is None:
        return Product.objects.all()
    if Category.objects.filter(id=category_id).exists():
        category = Category.objects.get(id=category_id)
    else:
        return []
    if category is None:
        return []
    return category.products.all()


def find_modification(product, modification_dict):  # #Ищет конкретную модификацию по набору параметров и продукту
    modifications = Modification.objects.filter(product=product)
    for modification in modifications:
        current_modification_dict = literal_eval(modification.characteristics)
        if current_modification_dict == modification_dict:
            return modification
    return None


def find_stock_product(product, modification_dict):  # #Ищет сток продукт по набору параметров и продукту
    modification = find_modification(product, modification_dict)
    stock_product = StockProduct.objects.get(product=product, modification=modification)
    return stock_product


@csrf_exempt
def get_images_of_stock_product(request):
    if request.method != 'POST' or 'product_id' not in request.POST or 'modification_dict_str' not in request.POST:
        raise NotImplementedError
    product = Product.objects.get(id=request.POST.get('product_id'))
    modification_dict = literal_eval(request.POST.get('modification_dict_str'))
    stock_product = find_stock_product(product, modification_dict)
    images = stock_product.images.all()
    data = dict()
    for i in range(len(images)):
        data[str(i)] = images[i].image.url
    return JsonResponse(data)


def get_product_modification_parameters(product):  # #Передает параметры модификаций данного продукта
    sample_modification = product.modifications.all()[0]
    sample_characteristics = sample_modification.characteristics
    sample_char_dict = literal_eval(sample_characteristics)
    parameters_list = list()
    for key, value in sample_char_dict.items():
        parameters_list.append(key)
    return parameters_list


def get_modification_parameter_values(product, parameter):  # #Возвращает все возможные значения параметра модификации
    modifications = product.modifications.all()
    values = []
    for modification in modifications:
        modification_dict = literal_eval(modification.characteristics)
        if parameter not in modification_dict:
            raise NotImplementedError
        value = modification_dict[parameter]
        if value not in values:
            values.append(value)
    return values


def get_modifications_dict(product):  # #Возвращает параметры модификации и их возможные значения в виде словаря
    mod_dict = dict()
    parameters = get_product_modification_parameters(product)
    for parameter in parameters:
        mod_dict[parameter] = get_modification_parameter_values(product, parameter)
    return mod_dict


def get_modifications_json(request):  # #Возвращает параметры модификации и их возможные значения в JSON
    if not request.method == 'GET' or 'product_id' not in request.GET:
        raise NotImplementedError
    product = Product.objects.get(id=request.GET.get('product_id'))
    mod_dict = get_modifications_dict(product)
    return JsonResponse(mod_dict)


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
    for products in cart:
        print(str(products['stock_product']) + ' ' + str(stock_product.id))
        if int(products['stock_product']) == int(stock_product.id):
            if int(quantity) + int(products['quantity']) > stock_product.quantity:
                raise ValueError
            else:
                products['quantity'] = int(quantity) + int(products['quantity'])
                return
    if int(quantity) > stock_product.quantity:
        raise ValueError
    cart.append(model_to_dict(order_product_info))


"""
В запросе через скрытое поле должне передаваться id продукта
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
            try:
                __add_to_cart_unauthenticated__(quantity, stock_product, request.session['cart'])
            except ValueError:
                e_handler500(request)
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
И удаление текущей корзины.
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
            order.save()
            for order_product in order_products:
                order_product.order = order
                order_product.save()
            return redirect('/profile')
        else:
            if 'cart' not in request.session or len(request.session['cart']) == 0:
                raise NotImplementedError
            try:
                address = request.session['address']
            except KeyError:
                raise KeyError # # Лучше переработать
            email = request.POST.get('email')
            current_cart = request.session['cart']
            if address is None or email is None:
                raise ValueError # # Лучше переработать
            city = address['city']
            street = address['street']
            building = address['building']
            flat = address['flat']
            entrance = address['entrance']
            if Addresses.objects.filter(city=city, street=street, building=building, flat=flat, entrance=entrance).exists():
                ad = Addresses.objects.get(city=city, street=street, building=building, flat=flat, entrance=entrance)
            else:
                ad = Addresses(city=city,
                               street=street,
                               building=building,
                               flat=flat,
                               entrance=entrance)
                ad.save()
            order = Order(email=email, address=ad)
            order.save()
            for order_product_information in current_cart:
                order_product = OrderProduct(quantity=order_product_information['quantity'],
                                             stock_product=StockProduct.objects.get(id=order_product_information['stock_product']),
                                             order=order)
                order_product.save()
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


def add_address_unauth(request):
    if request.method == 'POST' and not request.user.is_authenticated:
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
                request.session['address'] = model_to_dict(ad)
            else:
                new_ad = Addresses(city=city,
                                   street=street,
                                   building=building,
                                   flat=flat,
                                   entrance=entrance)
                request.session['address'] = model_to_dict(new_ad)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) # #Возможно, редерикт на страницу оформления заказа
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
        address_id = int(request.POST.get('id'))
        address = Addresses.objects.get(id=address_id)
        user.addresses_set.remove(address)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('/')


@login_required
def profile_addresses(request):
    user = request.user
    addresses = user.addresses_set.all()
    context = dict()
    context['addresses'] = addresses
    context['form'] = AddressForm()
    return render(request, 'addresses.html', context)


@login_required
def make_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            author = request.user
            content = form.cleaned_data['content']
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
    return render(request, 'registration/profile.html')

@login_required
def profile_orders(request):
    return render(request, 'registration/profile_orders.html')


#
