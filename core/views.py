from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from core.models import Category, Cart, OrderProduct, Order,\
    Addresses, Product, Question, StockProduct, Modification, OrderProductInformation, Image
from django.core.exceptions import ObjectDoesNotExist
from ast import literal_eval
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from core.forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from core.token import account_activation_token, confirm_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.forms.models import model_to_dict
from core.forms import AddressForm, ProfileForm, PasswordProfileForm, QuestionForm,\
    ProfileAddressForm, AddImgForm, AddSeveralImgForm
import itertools


@login_required
def admin_page(request):
    if request.user.is_staff:
        return render(request, 'admin/admin_index.html')
    return redirect('/')


def product_page(request):
    if request.user.is_staff:
        return render(request, 'admin/product_page.html')
    return redirect('/')


def add_product(request):
    if request.user.is_staff:
        cat = return_categories()
        return render(request, 'admin/add_product.html', {'categories': cat})
    return redirect('/')


def change_product(request):
    if request.user.is_staff:
        cat = return_categories()
        id = request.GET.get('id')
        prod = Product.objects.get(id=id)
        scat = prod.categories
        return render(request, 'admin/change_product.html', {'categories': cat, 'self_cat': scat, 'prod': prod})
    return redirect('/')


def get_categories_id(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        prod = Product.objects.get(id=id)
        scat = prod.categories.all()
        data = dict()
        data['cat'] = []
        data['name'] = prod.name
        for cat in scat:
            data['cat'].append(str(cat.name))
        return JsonResponse(data)
    else:
        return redirect('/')


def change_exist_product(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        categories = request.POST.getlist('cat[]')
        main_cat = request.POST.get('main')
        name = request.POST.get('name')
        price = request.POST.get('price')
        rating = request.POST.get('rating')
        product = Product.objects.get(id=id)
        product.categories.clear()
        product.name= name
        product.main_category = Category.objects.get(name=main_cat)
        product.price = price
        if rating != '':
            product.rating = rating
        for cat in categories:
            if not product.categories.filter(name=cat).exists():
                category = Category.objects.get(name=cat)
            product.categories.add(category)
            cur_cat = category.parent_category
            while cur_cat != None:
                if not product.categories.filter(name=cur_cat.name).exists():
                    product.categories.add(cur_cat)
                cur_cat = cur_cat.parent_category
        product.save()
        return HttpResponse('Gacha')
    else:
        return redirect('/')


def form_product(request):
    if request.method == 'POST':
        categories = request.POST.getlist('cat[]')
        main_cat = request.POST.get('main')
        name = request.POST.get('name')
        price = request.POST.get('price')
        rating = request.POST.get('rating')
        if rating != '' :
            product = Product(name=name, price=price, rating = rating, main_category=Category.objects.get(name=main_cat))
        else:
            product = Product(name=name, price=price, main_category=Category.objects.get(name=main_cat))
        product.save()
        for cat in categories:
            if not product.categories.filter(name=cat).exists():
                category = Category.objects.get(name=cat)
            product.categories.add(category)
            cur_cat = category.parent_category
            while cur_cat != None:
                if not product.categories.filter(name=cur_cat.name).exists():
                    product.categories.add(cur_cat)
                cur_cat = cur_cat.parent_category
        return HttpResponse('Gacha')
    else:
        return redirect('/')


def category_page(request):
    if request.user.is_staff:
        return render(request, 'admin/category_page.html')
    return redirect('/')


def add_category(request):
    if request.user.is_staff:
        cat = return_categories()
        return render(request, 'admin/add_category.html', {'categories': cat})
    return redirect('/')


def category_list(request):
    if request.user.is_staff:
        cat = return_categories()
        return render(request, 'admin/category_list.html', {'categories': cat})
    return redirect('/')


def form_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        par = request.POST.get('parent')
        if par != '':
            par_cat = Category.objects.get(name=par)
            category = Category(name=name, parent_category=par_cat)
        else:
            category = Category(name=name)
        category.save()
        return HttpResponse('Gacha')
    else:
        return redirect('/')


def change_category(request):
    if request.method == 'GET':
        cat = return_categories()
        id = request.GET.get('id')
        category = Category.objects.get(id=id)
        return render(request, 'admin/change_category.html', {'cat': cat, 'category': category})
    else:
        return redirect('/')


def delete_category(request):
    if request.method == 'POST' and 'category_name' in request.POST:
        category_name = request.POST.get('category_name')
        category = Category.objects.filter(name=category_name)[0]
        category.delete()
        return JsonResponse({'result': 'success'})


def get_category_id(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        category = Category.objects.get(id=id)
        data = dict()
        data['name'] = category.name
        return JsonResponse(data)
    else:
        return redirect('/')


def change_exist_category(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        category = Category.objects.get(id=id)
        if request.POST.get('parent') != '' and request.POST.get('parent') != category.name:
            category.parent_category = Category.objects.get(name=request.POST.get('parent'))
        else:
            category.parent_category = None
        category.name = request.POST.get('name')
        category.save()
        return HttpResponse('Gacha')
    else:
        return redirect('/')


def get_product_by_name(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        prod = Product.objects.get(name=name)
        data = dict()
        data['id'] = prod.id
        return JsonResponse(data)
    return redirect('/')


def modification_page(request):
    if request.user.is_staff:
        return render(request, 'admin/modification_page.html')
    return redirect('/')


def find_product(request):
    if request.user.is_staff:
        products = Product.objects.all()
        return render(request, 'admin/find_product.html', {'products': products})
    return redirect('/')


def add_modification(request):
    if request.user.is_staff:
        return render(request, 'admin/add_modification.html')
    return redirect('/')


def form_modifications(request):
    if request.method == 'POST':
        char_names = request.POST.getlist('characteristics[]')
        print(char_names)
        values = request.POST.getlist('values[]')
        endval = []
        for i in range(len(values)):
            endval.append([])
            str = values[i]
            endval[i] = str.split(',')
        prod = Product.objects.get(id=request.POST.get('id'))
        prod.modifications.clear()
        prod.stock_products.clear()
        for i in itertools.product(*endval):
            str = ''
            for j in range(len(char_names)):
                if j == 0:
                    str = '{'
                str += '\'' + char_names[j] + '\': '
                str += '\'' + i[j] + '\''
                if j != len(char_names) - 1:
                    str += ', '
                else:
                    str += '}'
            if str != '':
                mod = Modification(product=prod, characteristics=str)
                mod.save()
        return HttpResponse('Gacha')
    return redirect('/')


def decode_characteristics(prod):
    sample_mod = prod.modifications.all()[0].characteristics
    d = dict()
    d = literal_eval(sample_mod)
    ans = []
    for key in d:
        ans.append(key)
    return ans


def decode_values(prod, chars):
    ans = []
    for i in range(len(chars)):
        ans.append([])
    for mod in prod.modifications.all():
        d = literal_eval(mod.characteristics)
        it = 0
        for key in d:
            ans[it].append(d[key])
            it += 1
    for i in range(len(chars)):
        ans[i] = list(set(ans[i]))
    return ans


def have_modifications(request):
    if request.method == 'POST':
        prod = Product.objects.get(id=request.POST.get('id'))
        data = dict()
        data['have'] = True
        if len(prod.modifications.all()) == 0:
            data['have'] = False
        if data['have']:
            data['char'] = decode_characteristics(prod)
            data['values'] = decode_values(prod, data['char'])
        return JsonResponse(data)
    return redirect('/')


def stock_product_page(request):
    if request.user.is_staff:
        products = Product.objects.all()
        return render(request, 'admin/stock_product_page.html', {'products': products})
    return redirect('/')


def add_stock_product(request):
    if request.user.is_staff:
        return render(request, 'admin/add_stock_product.html')
    return redirect('/')


def get_product_modifications(request):
    if request.method == 'POST':
        prod = Product.objects.get(id=request.POST.get('id'))
        data = dict()
        data['mod'] = []
        data['quantity'] = []
        data['ids'] = []
        for mod in prod.modifications.all():
            data['mod'].append(mod.characteristics)
            data['ids'].append(mod.id)
            if hasattr(mod, 'stock_product'):
                data['quantity'].append(mod.stock_product.quantity)
            else:
                data['quantity'].append(0)
        return JsonResponse(data)
    return redirect('/')


def get_product_stock_products(request):
    if request.method == 'POST':
        prod = Product.objects.get(id=request.POST.get('id'))
        data = dict()
        data['mod'] = []
        data['ids'] = []
        print(len(prod.stock_products.all()))
        for sp in prod.stock_products.all():
            data['mod'].append(sp.modification.characteristics)
            data['ids'].append(sp.id)
        return JsonResponse(data)
    return redirect('/')


def form_stock_products(request):
    if request.method == 'POST':
        prod = Product.objects.get(id=request.POST.get('id'))
        ids = request.POST.getlist('ids[]')
        q = request.POST.getlist('qs[]')
        for i in range(len(ids)):
            mod = Modification.objects.get(id=ids[i])
            if hasattr(mod, 'stock_product'):
                sp = mod.stock_product
                sp.quantity = q[i]
                sp.product = prod
                sp.save()
            else:
                sp = StockProduct(product=prod, modification=mod, quantity=q[i])
                sp.save()
        return HttpResponse('Gacha')
    return redirect('/')


def find_prod_for_img(request):
    if request.user.is_staff:
        products = Product.objects.all()
        return render(request, 'admin/find_prod_for_img.html', {'products': products})
    return redirect('/')


def product_page_img(request):
    if request.user.is_staff:
        prod = Product.objects.get(id=request.GET.get('id'))
        has_img = hasattr(prod, 'image')
        if request.method == 'POST':
            form = AddImgForm(request.POST, request.FILES)
            if form.is_valid():
                if has_img:
                    prod_img = prod.image
                    prod_img.delete()
                if 'img' in request.FILES and request.FILES['img'] != None:
                    img = request.FILES['img']
                    image = Image(image=img, product=prod)
                    image.save()
                return HttpResponseRedirect('/')
        else:
            form = AddImgForm()
        return render(request, 'admin/product_img.html', {'form': form, 'prod': prod, 'img': has_img})
    return redirect('/')


def find_out_what_stock_product(request):
    if request.user.is_staff:
        prod = Product.objects.get(id=request.GET.get('id'))
        sp = prod.stock_products.all()
        return render(request, 'admin/find_stock_pr.html', {'sp': sp})
    return redirect('/')


def stock_product_images(request):
    if request.user.is_staff:
        sp = StockProduct.objects.get(id=request.GET.get('id'))
        has_img = hasattr(sp, 'images')
        images = []
        for imag in sp.images.all():
            images.append(imag.image.url)
        if request.method == 'POST':
            form = AddSeveralImgForm(request.POST, request.FILES)
            if form.is_valid():
                imags = request.FILES.getlist('img')
                for img in imags:
                    image = Image(image=img, stock_product=sp)
                    image.save()
                return HttpResponseRedirect('/admin/stock_products/img?id='+str(sp.product.id))
        else:
            form = AddSeveralImgForm()
        return render(request, 'admin/stock_product_img.html', {'form': form, 'sp': sp, 'img': has_img, 'images': images})
    return redirect('/')


def find_sp_images(request):
    if request.method == 'POST':
        sp = StockProduct.objects.get(id=request.POST.get('id'))
        data = dict()
        data['urls'] = []
        data['ids'] = []
        for img in sp.images.all():
            data['urls'].append(img.image.url)
            data['ids'].append(img.id)
        return JsonResponse(data)
    return redirect('/')


def delete_product(request):
    if request.method == 'POST':
        prod = Product.objects.get(id=request.POST.get('id'))
        prod.delete()
        return HttpResponse('Gacha')
    return redirect('/')


# # delete stock_product img
def del_img(request):
    if request.method == 'POST':
        img = Image.objects.get(id=request.POST.get('id'))
        id = request.POST.get('prod_id')
        prod = StockProduct.objects.get(id=id)
        prod.images.remove(img)
        return HttpResponse('Gacha')
    return redirect('/')


def orders_page(request):
    if request.user.is_staff:
        return render(request, 'admin/orders_page.html')
    return redirect('/')


def get_all_orders(request):
    if request.method == 'POST':
        orders = Order.objects.all()
        data = dict()
        data['id'] = []
        data['date'] = []
        data['author'] = []
        data['email'] = []
        data['status'] = []
        data['address'] = []
        for order in orders:
            data['id'].append(order.id)
            data['date'].append(order.order_date.strftime("%Y-%m-%d %H:%M"))
            if order.author != None:
                data['author'].append(order.author.username)
            else:
                data['author'].append('Незарегистрирован')
            data['email'].append(order.email)
            data['status'].append(order.status)
            data['address'].append(str(order.address))
        for i in range(len(data['id'])):
            j = i + 1
            while j < len(data['id']):
                if data['status'][i] == "Ожидает подтверждения":
                    if data['status'][j] == "Ожидает подтверждения":
                        if data['date'][i] < data['date'][j]:
                            swap_data(data['id'], data['date'], data['author'], data['email'], data['status'], data['address'], i, j)
                if data['status'][i] == "Подтвержден":
                    if data['status'][j] == "Ожидает подтверждения":
                       swap_data(data['id'], data['date'], data['author'], data['email'], data['status'], data['address'], i, j)
                    elif data['status'][j] == "Подтвержден":
                        if data['date'][i] < data['date'][j]:
                            swap_data(data['id'], data['date'], data['author'], data['email'], data['status'],
                                      data['address'], i, j)
                if data['status'][i] == "Доставлен":
                    if data['date'][i] < data['date'][j]:
                        swap_data(data['id'], data['date'], data['author'], data['email'], data['status'], data['address'], i, j)

                j += 1
        return JsonResponse(data)
    return redirect('/')


def swap_data(id, date, author, email, status, address, i, j):
    id[i], id[j] = id[j], id[i]
    date[i], date[j] = date[j], date[i]
    author[i], author[j] = author[j], author[i]
    email[i], email[j] = email[j], email[i]
    status[i], status[j] = status[j], status[i]
    address[i], address[j] = address[j], address[i]


def change_order_status(request):
    if request.method == 'POST':
        order = Order.objects.get(id=request.POST.get('id'))
        status = request.POST.get('state')
        order.status = status
        order.save()
        return HttpResponse('Gacha')
    return redirect('/')


def user_list(request):
    if request.user.is_staff:
        return render(request, 'admin/user_list.html')
    return redirect('/')


def get_users(request):
    if request.method == 'POST':
        users = User.objects.all()
        data = dict()
        data['login'] = []
        data['email'] = []
        data['is_staff'] = []
        data['id'] = []
        for user in users:
            if user != request.user:
                data['email'].append(user.email)
                data['login'].append(user.username)
                data['is_staff'].append(user.is_staff)
                data['id'].append(user.id)
        print(data['id'])
        return JsonResponse(data)
    return redirect('/')


def change_user_rights(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        user = User.objects.get(id=id)
        if request.POST.get('is_staff') == 'true':
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()
    return redirect('/')


def del_user(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        user = User.objects.get(id=id)
        user.delete()
        return HttpResponse('Gacha')
    return redirect('/')


def clear_session(request):
    request.session.flush()
    return redirect('/')


def print_unauth_cart(request):
    if 'cart' not in request.session:
        print('cart: None')
    else:
        print('cart: ', request.session['cart'])


def arr_to_str(arr):
    string = str()
    for element in arr:
        string += str(element) + ','
    string = string[:(len(string) - 1)]
    return string


def dict_cart_to_model_cart(dict_cart):
    model_cart = list()
    for i in range(len(dict_cart)):
        stock_product = StockProduct.objects.get(id=int(dict_cart[i]['stock_product']))
        order_product_info = OrderProductInformation(quantity=int(dict_cart[i]['quantity']),
                                                     stock_product=stock_product)
        order_product_info.id = i
        model_cart.append(order_product_info)
    return model_cart


def js_string_to_arr(js_string):
    if js_string == '[]':
        return []
    ids_string = js_string
    ids_string = ids_string[1:(len(ids_string) - 1)]
    ids_array = ids_string.split(', ')
    return ids_array


def index_page(request):
    """
    Обработка главной страницы

        \n:param request: Запрос\
        \n:return: Обработанная HTML-страница\

    \nКонтекст:

        \n:param is_category: Надо ли отобразить конкретную категорию\
        \n:param category_name: Имя категории, которую надо отобразить\
        \n:param is_search: Надо ли делать поисковой запрос\
        \n:param search_query: Поисковой запрос, если он имеется\
        \n:param products: Список продуктов для отображения\
        \n:param is_empty: Пуст ли список продуктов для отображения\

    """
    context = dict()
    if 'category_id' in request.GET:
        category_id = request.GET.get('category_id')
        if Category.objects.filter(id=category_id).exists():
            category = Category.objects.get(id=category_id)
        else:
            return e_handler500(request)
        context['is_category'] = True
        context['category_name'] = category.name
    else:
        category_id = None
        context['is_category'] = False
    if 'text' in request.GET:
        text = request.GET.get('text')
        context['search_query'] = text
        context['is_search'] = True
    else:
        text = None
        context['is_search'] = False
    context['products'] = return_products(category_id=category_id, search_query=text)
    if len(context['products']) == 0:
        context['is_empty'] = True
    else:
        context['is_empty'] = False

    return render(request, 'index.html', context)


def e_handler500(request):
    response = render_to_response('error500.html')
    response.status_code = 500
    return response


def product_names_json(request):
    data = dict()
    data['product_names'] = []
    for product in Product.objects.all():
        data['product_names'].append(product.name)
    return JsonResponse(data)


def cart_page(request):
    """
    Обработка страницы корзины

        \n:param request: Запрос\
        \n:return: Обработанная HTML-страница\

    \nКонтекст:

        \n:param ids: Список id объектов OrderProduct из корзины\
        \n:param order_products: Объекты OrderProduct из корзины\
        \n:param is_empty: Пуста ли корзина\
        \n:param is_auth: Зарегистрирован ли текущий пользователь\

    """
    context = dict()
    cart = list()
    if request.user.is_authenticated:
        user = request.user
        try:
            cart = user.cart.products.all()
        except ObjectDoesNotExist:
            new_cart = Cart(author=user)
            new_cart.save()
            cart = new_cart.products.all()
    else:
        if 'cart' not in request.session:
            request.session['cart'] = list()
        cart = dict_cart_to_model_cart(request.session['cart'])

    context['ids'] = []
    context['order_products'] = cart
    for i in range(len(cart)):
        context['ids'].append(cart[i].id)

    context['is_empty'] = False
    if len(cart) == 0:
        context['is_empty'] = True

    context['is_auth'] = request.user.is_authenticated

    return render(request, 'cart.html', context)


def get_order_product_info_json(request):  # #Передается массив из order_product.id
    """
    Возвращение информации об объектах OrderProduct

        \n:param request: Запрос\
        \n:return: Словарь в виде JSON, содержащий информацию об объектах OrderProduct\

    \nСодержание запроса:

        \n:param order_product_id: Строка, кодирующая массив из ID объектов OrderProduct. Преобразуется в массив
                            посредством метода js_string_to_arr\

    \nСодержание JSON:
    \nПервым ключем в словаре служит ID соответствующего OrderProduct

        \n:param modifications: Словарь из модификаций продукта\
        \n:param quantity: Количество продукта в OrderProduct\
        \n:param max_quantity: Количество продукта на складе\
        \n:param name: Название продукта\
        \n:param price: Цена продукта\
        \n:param image_url: Ссылка на превью-изображение продукта\
        \n:param stock_product_id: ID соответствующего складового продукта\
    """
    if request.method != 'POST' or 'order_product_id' not in request.POST:
        raise NotImplementedError

    info_dict = dict()
    info_dict['order_product_ids'] = js_string_to_arr(request.POST.get('order_product_id'))

    for order_product_id in info_dict['order_product_ids']:
        info_dict[order_product_id] = dict()

        if request.user.is_authenticated:
            order_product = OrderProduct.objects.get(id=order_product_id)
            stock_product = order_product.stock_product
            quantity = order_product.quantity
        else:
            order_product_dict = request.session['cart'][int(order_product_id)]
            stock_product = StockProduct.objects.get(id=int(order_product_dict['stock_product']))
            quantity = int(order_product_dict['quantity'])

        modifications = stock_product.modification.characteristics
        info_dict[order_product_id]['modifications'] = literal_eval(modifications)
        info_dict[order_product_id]['quantity'] = quantity
        info_dict[order_product_id]['max_quantity'] = stock_product.quantity
        info_dict[order_product_id]['name'] = stock_product.product.name
        info_dict[order_product_id]['price'] = stock_product.product.price
        info_dict[order_product_id]['image_url'] = stock_product.product.image.image.url
        info_dict[order_product_id]['stock_product_id'] = stock_product.id

    return JsonResponse(info_dict)


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


def return_categories():
    return Category.objects.all()


def return_categories_json(request):
    """
    Возвращение информации о категориях в виде JSON

        \n:param request: Запрос\
        \n:return: Строка с описанием категорий, включенная в JSON-словарь\

    \nСодержание JSON:
    \n Под ключем '1' хранится строка, содержащая информацию о всех категориях в виде\
    \n 'category_id, category_name, parent_category_id;', если есть родительская категория, или\
    \n 'category_id, category_name, None;', если родительской категории нет.\

    """
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


def browse_product(request):
    """
    Обработка страницы товара

        \n:param request: Запрос\
        \n:return: Обработанная HTML-страница\

    \nСодержание запроса:

        \n:param id: ID отображаемого продукта\

    \nКонтекст:

        \n:param product: Объект Product, соответствующий отображаемому продукту\


    """
    context = dict()
    if request.method == 'GET':
        if 'id' in request.GET:
            product = Product.objects.get(id=request.GET['id'])
            context['product'] = product
            return render(request, 'product_page.html', context)
    return render(request, 'index.html', context)


def return_products(category_id=None, search_query=None):
    """
    Возвращение продуктов для главной страницы

        \n:param category_id: ID выбранной категории (если есть)\
        \n:param search_query: Поисковой запрос (если есть)\
        \n:return: Массив продуктов из искомой категории, удовлетворяющих поисковому запросу\
    """
    if category_id is None and search_query is None:
        return Product.objects.all()
    if category_id is None:
        return search_in_base(search_query)
    category = Category.objects.get(id=category_id)
    category_products = category.products.all()
    if search_query is None:
        return category_products
    found_products = search_in_base(search_query)
    return set(found_products).intersection(category_products)


def find_modification(product, modification_dict):
    """
    Поиск конкретной модификации в базе данных по набору параметров и продукту

        \n:param product: Объект Product, к которому привязана модификация\
        \n:param modification_dict: Словарь вида {parameter: value}, кодирующий модификацию\

        \n:return: Искомая модификация (если она есть) или None (если ее нет)\
    """
    modifications = Modification.objects.filter(product=product)
    for modification in modifications:
        current_modification_dict = literal_eval(modification.characteristics)
        if current_modification_dict == modification_dict:
            return modification
    return None


def find_stock_product(product, modification_dict):
    """
    Поиск складового продукта по продукту и словарю модификации

        \n:param product: Продукт, к которому привязан складовой продукт\
        \n:param modification_dict: Словарь вида {parameter: value}, кодирующий модификацию\
        \n:return: Складовой продукт (если он найден) или None (если ничего не найдено)

    """
    modification = find_modification(product, modification_dict)
    try:
        stock_product = StockProduct.objects.get(product=product, modification=modification)
    except ObjectDoesNotExist:
        stock_product = None
    return stock_product


def get_images_of_stock_product(request):
    """
    Получение изображений складового продукта и его количества

        \n:param request: Пост-запрос\
        \n:return: JSON-словарь с изображениями складового продукта\

    \nСодержание запроса:

        \n:param product_id: ID объекта Product, к которому привязан складовой продукт\
        \n:param modification_dict_str: Строка, содержащая в себе словарь модификации\

    \nСодержание JSON:

        \n:param images: Массив из ссылок на изображения складового продукта\
        \n:param quantity: Количество продуктов на складе\
    """
    if request.method != 'POST' or 'product_id' not in request.POST or 'modification_dict_str' not in request.POST:
        raise NotImplementedError
    product = Product.objects.get(id=request.POST.get('product_id'))
    modification_dict = literal_eval(request.POST.get('modification_dict_str'))
    stock_product = find_stock_product(product, modification_dict)
    images = stock_product.images.all()
    data = dict()
    data['images'] = list()
    for i in range(len(images)):
        data['images'].append(images[i].image.url)
    data['quantity'] = stock_product.quantity
    return JsonResponse(data)


def get_product_modification_parameters(product):
    """
    Возвращение параметров модификации данного продукта

        \n:param product: Объект Product\
        \n:return: Список из параметров, по которым меняются модификации для данного продукта\
    """
    sample_modification = product.modifications.all()[0]
    sample_characteristics = sample_modification.characteristics
    sample_char_dict = literal_eval(sample_characteristics)
    parameters_list = list()
    for key, value in sample_char_dict.items():
        parameters_list.append(key)
    return parameters_list


def get_modification_parameter_values(product, parameter):
    """
    Возвращение возможных значения данного параметра модификации

        \n:param product: Объект Product\
        \n:param parameter: Конкретный параметр модификации\
        \n:return: Список из всех возможных значения для данного параметра модификации\
    """
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


def get_modifications_dict(product):
    """
    Возвращение всех параметров модификаций и их значений в виде словаря

        \n:param product: Объект product\
        \n:return: Словарь, ключами которого служат параметры, а в mod_dict[parameter] лежит список из возможных
                    значений данного параметра
    """
    mod_dict = dict()
    parameters = get_product_modification_parameters(product)
    for parameter in parameters:
        mod_dict[parameter] = get_modification_parameter_values(product, parameter)
    return mod_dict


def get_modifications_json(request):
    """
    Возвращение всех параметров модификаций и их значений в виде JSON

        \n:param request: Гет-запрос\
        \n:return: JSON-словарь, по структуре аналогичный словарю из get_modifications_dict(product)\

    \nСодержание запроса:

        \n:param product_id: ID объекта Product\

    """
    if not request.method == 'GET' or 'product_id' not in request.GET:
        raise NotImplementedError
    product = Product.objects.get(id=request.GET.get('product_id'))
    mod_dict = get_modifications_dict(product)
    return JsonResponse(mod_dict)


def __add_to_cart_authenticated__(user, quantity, stock_product):
    """
    Добавление складового продукта в корзину зарегистрированного пользователя

        \n:param user: Пользователь\
        \n:param quantity: Количества продукта, которое надо добавить\
        \n:param stock_product: Объект StockProduct\
        \n:raises ValueError: Если количество продукта больше, чем есть на складе\
    """
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
            prod.refresh_cost()
            prod.save()
    else:
        if int(quantity) > stock_product.quantity:
            raise ValueError
        else:
            order_product = OrderProduct()
            order_product.quantity = int(quantity)
            order_product.stock_product = stock_product
            order_product.cart = current_cart
            order_product.refresh_cost()
            order_product.save()


def __add_to_cart_unauthenticated__(quantity, stock_product, cart):
    """
    Добавление складового продукта в корзину незарегистрированного пользователя

        \n:param quantity: Количество продукта, которое надо добавить\
        \n:param stock_product: Объект StockProduct\
        \n:param cart: Список, служащий корзиной для данного пользователя\
        \n:raises ValueError: Если количество продукта больше, чем есть на складе\
    """
    order_product_info = OrderProductInformation(quantity=quantity, stock_product=stock_product)
    for products in cart:
        if int(products['stock_product']) == int(stock_product.id):
            if int(quantity) + int(products['quantity']) > stock_product.quantity:
                raise ValueError
            else:
                products['quantity'] = int(quantity) + int(products['quantity'])
                return
    if int(quantity) > stock_product.quantity:
        raise ValueError
    cart.append(model_to_dict(order_product_info))


def add_to_cart(request):
    """
    Добавление складового продукта в корзину пользователя

        \n:param request: Пост-запрос\
        \n:return: HttpResponse 'success', если добавление прошло удачно, или ошибку500, если количество продукта
        слишком большое\
        \n:raises NotImplementedError: Если в запросе не прописаны значения для каждого из параметров модификации\

    \nСодержание запроса:

        \n:param quantity: Количество продукта, которое надо добавить\
        \n:param product_id: ID объекта Product\
        \n:param request.session['cart']: Корзина незарегистрированного пользователя, хранящаяся в сессии\

        Для каждого параметра модификации:

            \n:param modification_parameter: Значение параметра для модификации, которую надо добавить в корзину\


    """
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
                return e_handler500(request)
        else:
            if 'cart' not in request.session:
                request.session['cart'] = []
            try:
                __add_to_cart_unauthenticated__(quantity, stock_product, request.session['cart'])
            except ValueError:
                return e_handler500(request)
        return HttpResponse('success')


def delete_from_cart(request):
    """
    Удаление складового продукта из корзины

        \n:param request: Пост-запрос\
        \n:return: HttpResponse 'success', если удаление прошло удачно, или HttpResponse 'failed', если при удалении
        произошла ошибка\

    \nСодержание запроса:

        \n:param stock_product_id: ID объекта StockProduct, который надо удалить из корзины\
        \n:param user: Пользователь (если пользователь зарегистрирован)\
        \n:param request.session['cart']: Корзина незарегистрированного пользователя, хранящаяся в сессии\
    """
    if request.method == 'POST':
        stock_product_id = int(request.POST.get('stock_product_id'))
        try:
            stock_product = StockProduct.objects.get(id=stock_product_id)
            if request.user.is_authenticated:
                user = request.user
                order_product = user.cart.products.get(stock_product=stock_product)
                order_product.delete()
            else:
                for order_product_dict in request.session['cart']:
                    if order_product_dict['stock_product'] == stock_product.id:
                        request.session['cart'].remove(order_product_dict)
            return HttpResponse('success')
        except ObjectDoesNotExist:
            return HttpResponse('failed')
    return redirect('/')


def clear_cart(request):
    """
    Отчистка корзины

        \n:param request: Пост-запрос, содержащий текущего пользователя (если он зарегистрирован) и корзину
        незарегистрированного пользователя в сессии\

        \n:return: HttpResponse 'success', если отчистка прошла удачно\
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            request.user.cart.delete()
            cart = Cart(author=request.user)
            cart.save()
            return HttpResponse('success')
        else:
            clear_session(request)
            return HttpResponse('success')


def __cart_from_session_to_db__(current_cart, user):
    for information in current_cart:
        quantity = information['quantity']
        stock_product = StockProduct.objects.get(id=information['stock_product'])
        __add_to_cart_authenticated__(user, quantity, stock_product)


def change_order_product_quantity(request):
    """
    Изменение количества в объекте OrderProduct (для изменения количества товара в корзине)
        \n:param request: Пост-запрос\
        \n:return: HttpResponse 'success' при удачном изменении, или HttpResponse 'invalid quantity' при неподходящем
        новом количестве товаров\

        \n:raises NotImplementedError: Если запрос не содержит все необходимые данные\

    \nСодержание запроса:

        \n:param new_quantity: Новое количество товара\
        \n:param stock_product_id: ID складового продукта, количество которого меняется\
        \n:param request.session['cart']: Корзина незарегистрированного пользователя в сессии\
    """
    if request.method != 'POST' or 'new_quantity' not in request.POST or 'stock_product_id' not in request.POST:
        raise NotImplementedError
    new_quantity = int(request.POST['new_quantity'])
    stock_product_id = int(request.POST['stock_product_id'])
    stock_product = StockProduct.objects.get(id=stock_product_id)
    if request.user.is_authenticated:
        order_product = request.user.cart.products.get(stock_product=stock_product)
        if 0 < new_quantity < stock_product.quantity:
            order_product.quantity = new_quantity
            order_product.refresh_cost()
            order_product.save()
            return HttpResponse('success')
        else:
            return HttpResponse('invalid quantity')
    else:
        index = None
        for i in range(len(request.session['cart'])):
            if request.session['cart'][i]['stock_product'] == stock_product_id:
                index = i
        if 0 < new_quantity < stock_product.quantity:
            request.session['cart'][index]['quantity'] = str(new_quantity)
            return HttpResponse('success')
        else:
            return HttpResponse('invalid quantity')


def confirm_order(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        order = Order.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError):
        order = None
    if order is not None and confirm_token.check_token(order, token):
        order.status = 'Подтвержден'
        order.save()
        messages.success(request, 'Вы успешно подтвердили свой заказ')
        return redirect('home')
    else:
        messages.error(request, 'Ссылка для подтвержения устарела')
        return redirect('home')


def validate_order(request, order):
    if request.user.is_authenticated:
        user = request.user
    current_site = get_current_site(request)
    mail_subject = 'Подтвердите ваш заказ'
    if request.user.is_authenticated:
        message = render_to_string('confirm_order.html', {
            'is_authenticated': True,
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(order.pk)).decode(),
            'token': confirm_token.make_token(order),
            'order': order.pk
        })
    else:
        message = render_to_string('confirm_order.html', {
            'is_authenticated': False,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(order.pk)).decode(),
            'token': confirm_token.make_token(order),
            'order': order.pk
        })
    if request.user.is_authenticated:
        to_email = order.author.email
    else:
        to_email = order.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()


def make_order(request):
    """
    Создание заказа

        \n:param request: Пост-запрос
        \n:return: HttpResponse 'success' или перенаправление на главную страницу, если все прошло успешно
        \n:raises NotImplementedError: Если запрос не содержит всю необходимую информацию
        \n:raises ValueError: Если с фронтенда передается неправильная форма

    \nСодержание запроса для зарегистрированного пользователя:

        \n:param user: Пользователь
        \n:param address_id: ID адреса, выбранного пользователем для доставки

    \nСодержание запроса для незарегистрированного пользователя:

        \n:param request.session['cart']: Корзина, хранящаяся в сессии
        \n:param city: Город
        \n:param street: Улица
        \n:param building: Строение
        \n:param flat: Номер квартиры
        \n:param entrance: Номер подъезда
        \n:param email: Электронная почта пользователя

    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            order_products = user.cart.products.all()
            if len(order_products) == 0:
                raise NotImplementedError
            address_id = int(request.POST.get('address_id'))
            address = Addresses.objects.get(id=address_id)
            order = Order(author=user,
                          address=address)
            order.save()
            validate_order(request, order)

            cost = 0
            for order_product in order_products:
                order_product.order = order
                cost += order_product.stock_product.product.price * order_product.quantity
                order_product.save()

                sp = order_product.stock_product
                sp.quantity -= order_product.quantity
                sp.save()

            order.cost = cost
            order.save()

            return HttpResponse('success')
        else:
            if 'cart' not in request.session or len(request.session['cart']) == 0:
                raise NotImplementedError
            city = request.POST.get('city')
            street = request.POST.get('street')
            building = request.POST.get('building')
            flat = request.POST.get('flat')
            entrance = request.POST.get('entrance')
            address = Addresses(city=city,
                                street=street,
                                building=building,
                                flat=flat,
                                entrance=entrance)
            address.save()
            email = request.POST.get('email')
            current_cart = request.session['cart']
            if address is None or email is None:
                raise ValueError
            order = Order(email=email, address=address)
            order.save()

            validate_order(request, order)

            cost = 0
            for order_product_information in current_cart:
                order_product = OrderProduct(quantity=order_product_information['quantity'],
                                             stock_product=StockProduct.objects.get(id=order_product_information['stock_product']),
                                             order=order)
                order_product.refresh_cost()
                stock_product = StockProduct.objects.get(id=order_product_information['stock_product'])
                stock_product.quantity -= int(order_product_information['quantity'])
                stock_product.save()
                order_product.save()
                cost += int(order_product.cost)
            order.cost = cost
            order.save()

            return redirect('/')
    return redirect('/')


@login_required
def view_order(request):
    """
    Обработка страницы отображения заказа

        \n:param request: Гет-запрос
        \n:return: Обработанная HTML-страница, если все прошло успешно, или ошибка500 при возникновении ошибки

    \nСодержание запроса:

        \n:param id: ID заказа
        \n:param user: Пользователь

    \nКонтекст:

        \n:param ids: Список из ID объектов OrderProduct, входящих в состав заказа
        \n:param order_products: Список из объектов OrderProduct, входящих в состав заказа
        \n:param order_cost: Стоимость заказа
        \n:param order_id: ID заказа
    """
    if request.method == 'GET':
        if 'id' not in request.GET:
            return e_handler500(request)
        order_id = int(request.GET.get('id'))
        has_permission = False
        user = request.user
        if user.is_superuser:
            has_permission = True
        else:
            for order in user.orders.all():
                print(order.id, order_id)
                if order.id == order_id:
                    has_permission = True
        if not has_permission:
            return e_handler500(request)
        order = Order.objects.get(id=order_id)
        context = dict()
        context['ids'] = list()
        context['order_products'] = order.products.all()
        context['order_cost'] = order.cost
        context['order_id'] = order_id
        for order_product in order.products.all():
            context['ids'].append(order_product.id)
        return render(request, 'order.html', context)
    return e_handler500(request)


@login_required
def profile_info(request):
    return render(request, 'profile.html')


@login_required
def get_addresses_json(request):
    """
    Получение адресов пользователя в виде JSON
        \n:param request: Пост-запрос
        \n:return: JSON-словарь вида {address_id: address_description}
    """
    if request.method == 'POST':
        user = request.user
        response = dict()
        for address in user.addresses.all():
            response[address.id] = address.description
        return JsonResponse(response)


@login_required
def add_address(request):
    """
    Добавление адреса в список адресов зарегистрированного пользователя на странице создания заказа

        \n:param request: Пост-запрос
        \n:return: JSON {'result': 'success'} при успешном выполнении, JSON {'result': 'fail'} при возникновении ошибки
        в процессе выполнения, или JSON {'result': 'found description'}, если адрес с введенным пользователем
        описанием уже был в списке адресов этого пользователя

    \nСодержание запроса:

        \n:param user: Пользователь
        \n:param city: Город
        \n:param street: Улица
        \n:param building: Строение
        \n:param flat: Номер квартиры
        \n:param entrance: Номер подъезда
        \n:param description: Описание адреса

    """
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            city = form.cleaned_data['city']
            street = form.cleaned_data['street']
            building = form.cleaned_data['building']
            flat = form.cleaned_data['flat']
            entrance = form.cleaned_data['entrance']
            description = form.cleaned_data['description']
            found = False
            found_description = False
            for ad in user.addresses.all():
                if ad.city == city and ad.street == street and ad.building == building and ad.flat == flat and ad.entrance == entrance:
                    found = True
                if ad.description == description:
                    found_description = True
            if found_description:
                return JsonResponse({'result': 'found description'})
            if not found:
                new_ad = Addresses(city=city,
                                   street=street,
                                   building=building,
                                   flat=flat,
                                   entrance=entrance,
                                   description=description)
                new_ad.customer = user
                new_ad.save()

            return JsonResponse({'result': 'success'})
        else:
            return JsonResponse({'result': 'fail'})


@login_required
def add_address_user(request):
    """
    Добавление адреса в список адресов зарегистрированного пользователя в Личном кабинете

        \n:param request: Пост-запрос
        \n:return: Перенаправление на страницу адресов в Личном кабинете

    \nСодержание запроса:

        \n:param user: Пользователь
        \n:param city: Город
        \n:param street: Улица
        \n:param building: Строение
        \n:param entrance: Номер подъезда
        \n:param flat: Номер квартиры
        \n:param description: Описание адреса
    """
    if request.method == "POST":
        form_address = AddressForm(request.POST)

        city = form_address.data.get('city')
        street = form_address.data.get('street')
        building = form_address.data.get('building')
        entrance = form_address.data.get('entrance')
        flat = form_address.data.get('flat')
        description = form_address.data.get('description')

        found_description = False
        for ad in request.user.addresses.all():
            if ad.description == description:
                found_description = True
        if found_description:
            return HttpResponse('У вас уже существует адрес с таким описанием\
             <a href="/accounts/addresses/">Вернуться</>')

        address_new = Addresses(city=city, street=street, building=building, flat=flat, entrance=entrance,
                                description=description)
        address_new.customer = request.user
        address_new.save()

    return redirect('profile_addresses')


@login_required
def delete_address(request):
    """
    Удаление адреса

        \n:param request: Пост-запрос
        \n:return: JSON {'result': 'success'} в случае успешного удаление и JSON {'result': 'permission denied}, если
        у пользователя нет прав на удаление этого адреса

    \nСодержание запроса:

        \n:param user: Пользователь
        \n:param id: ID адреса, подлежащего удалению
    """
    user = request.user
    user_addresses = user.addresses.all()
    if request.method == 'POST':
        address_id = int(request.POST.get('id'))
        address = Addresses.objects.get(id=address_id)
        if address in user_addresses:
            address.delete()
            return JsonResponse({'result': 'success'})
        return JsonResponse({'result': 'permission denied'})
    else:
        return redirect('/')


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
    """
    Регистрация нового пользователя

        \n:param request: Пост-запрос для регистрации и гет-запрос для отображения страницы
        \n:return: После регистрации: перенаправление на главную страницу и отправка письма с подтверждением аккаунта,
        до регистрации: отображение страницы регистрации

    \nСодержание запроса:

        \n:param SignupForm: В пост-запросе: Данные, необходимые для заполнения формы SignupForm (core.forms.SignupForm)
    """
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
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
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
    """
    Страница с отображением информации о пользователе

        \n:param request: Пост-запрос для изменения данных и гет-запрос для отображения данных
        \n:return: Возвращает сообщение об успешной смене данных и перенаправляет на исходную страницу

    \nОписание метода:

        Метод позволяет просмотреть текущую информацию о пользователей (имя, фамилия, электронная почта, пароль).
        Всю эту информацию, кроме электронной почты, можно изменить на этой же странице.
    """
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

    return render(request, 'registration/profile.html', {'form_name': form_name, 'form_password': form_password})


@login_required
def profile_orders(request):
    """
    Отображение таблицы заказов данного пользователя

        \n:param request: Запрос
        \n:return: Обработанная страница для отображения таблицы заказов

    \nКонтекст:

        \n:param empty: yes, если корзина пуста
        \n:param orders: Список заказов, если он не пуст
    """
    user = User.objects.get(username=request.user.username)
    orders = Order.objects.filter(author=user)

    if orders.count() == 0:
        return render(request, 'registration/profile_orders.html', {'empty': 'yes'})

    return render(request, 'registration/profile_orders.html', {'orders': orders})


@login_required
def profile_addresses(request):
    """
    Отображение страницы просмотра и редактирования адресов пользователя

        \n:param request: Гет-запрос для просмотра адресов и пост-запрос для редактирования адресов
        \n:return: Обработанная страница адресов

    \nСодержание гет-запроса:

        \n:param user: Пользователь
        \n:param id: ID конкретного адреса, если пользователь хочет его просмотреть

    \nКонтекст после гет-запроса:

        \n:param empty: yes, если список адресов пуст
        \n:param addresses: Список адресов
        \n:param form_address: Форма для редактирования адреса
        \n:param address: Конкретный адрес, если пользователь хочет просмотреть его
        \n:param id_: ID просматриваемого адреса

    \nСодержание пост-запроса:

        \n:param id_address: ID редактируемого адреса
        \n:param city: Новый город
        \n:param street: Новая улица
        \n:param building: Новое строение
        \n:param entrance: Новый номер подъезда
        \n:param flat: Новый номер квартиры
        \n:param description: Новое описание адреса
    """
    user = User.objects.get(username=request.user.username)
    addresses = user.addresses.all().filter(customer=user)

    form_address = ProfileAddressForm()

    if addresses.count() == 0:
        return render(request, 'registration/addresses.html', {'empty': 'yes', 'form_address': form_address})

    if request.method == 'GET':
        if request.GET.get('id'):
            form_address = ProfileAddressForm()
            data = request.GET.dict()
            id_ = int(data['id'])
            address = None
            for user_address in addresses:
                if user_address.id == id_:
                    address = user_address

            return render(request,  'registration/addresses.html',
                          {'addresses': addresses, 'form_address': form_address, 'address': address, 'id': id_})

    if request.method == 'POST':
        form_address = ProfileAddressForm(request.POST)

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

            return redirect('profile_addresses')

    return render(request, 'registration/addresses.html', {'addresses': addresses, 'form_address': form_address})


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
