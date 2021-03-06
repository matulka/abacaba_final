from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Product, Category, Cart, OrderProduct, Order,\
    Addresses, Product, Question, StockProduct, Modification
from django.core.exceptions import ObjectDoesNotExist
from core import views
from core.views import search_in_base
from django.test.client import RequestFactory
from django.forms.models import model_to_dict
import json


class TestUserCanSeePages(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()

    def test_user_can_see_index(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_user_can_see_cart(self):
        response = self.c.get('/cart')
        self.assertEqual(response.status_code, 200)

    def test_user_can_see_categories_page(self):
        response = self.c.get('/get_http_categories')
        self.assertEqual(response.status_code, 200)


class TestSearch(TestCase):

    def setUp(self):
        self.c = Client()
        self.cat = Category.objects.create(name='b')
        self.prod1 = Product.objects.create(name='abacaba',
                             price='1',
                             main_category=self.cat)
        self.prod2 = Product.objects.create(name='c',
                             price='1',
                             main_category=self.cat)

    def test_no_text(self):
        products = search_in_base('')
        self.assertEqual(len(products), 2)

    def test_no_result_1(self):
        products = search_in_base('ol')
        self.assertEqual(len(products), 0)

    def test_all_result(self):
        products = search_in_base('c')
        self.assertEqual(len(products), 2)

    def test_one_result(self):
        products = search_in_base('abac')
        self.assertEqual(len(products), 1)


class TestCategories(TestCase):

    def setUp(self):
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                             price='1',
                             main_category=self.cat1)
        self.prod1.categories.add(self.cat1)
        self.prod2 = Product.objects.create(name='c',
                             price='1',
                             main_category=self.cat1)
        self.prod2.categories.add(self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat2)

    def test_no_category(self):
        response = self.c.get('/', {'category_id': '0'})
        self.assertEqual(response.status_code, 500)

    def test_found_category1(self):
        response = self.c.get('/', {'category_id': '1'})
        self.assertEqual(len(response.context['products']), 2)

    def test_found_category2(self):
        response = self.c.get('/', {'category_id': '2'})
        self.assertEqual(len(response.context['products']), 0)


class TestAddresses(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()

    def test_del(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        response = self.c.post('/del_address',
                               {'id': 1})
        self.assertEqual(len(self.user.addresses.all()), 0)

    def test_adding(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        self.assertEqual(len(self.user.addresses.all()), 1)

    def test_add_two_simillar_1(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        self.assertEqual(len(self.user.addresses.all()), 1)

    def test_add_two_simillar_2(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        self.assertEqual(len(Addresses.objects.all()), 1)

    def can_see_addresses(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': '1', 'flat': '1', 'entrance': '1',
                                'description': 'kek'})
        response = self.c.post('/accounts/addresses')
        self.assertEqual(response.status_code, 200)


class TestQuestions(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()

    def test_add_question(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/make_question',
                               {'topic': 'test', 'content': 'text'})
        self.assertEqual(len(Question.objects.all()), 1)


class TestAddToCart(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                                            price='1',
                                            main_category=self.cat1)
        self.prod2 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat2)
        self.mod1 = Modification.objects.create(product=self.prod1,
                                            characteristics="{'a': '2', 'b': '3'}")
        self.mod2 = Modification.objects.create(product=self.prod2,
                                                characteristics="{'a': '3', 'b': '3'}")
        self.sp = StockProduct.objects.create(product=self.prod1,
                                                modification=self.mod1,
                                              quantity=5)
        self.sp1 = StockProduct.objects.create(product=self.prod2,
                                              modification=self.mod2,
                                              quantity=5)
        self.factory = RequestFactory()

    def test_auth_make_new_cart(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        self.assertEqual(len(self.user.cart.products.all()), 1)

    def test_auth_add_two_products(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        response = self.c.post('/add_to_cart', {'quantity': 1, 'product_id': 1, 'a': 2, 'b': 3})
        self.assertEqual(len(self.user.cart.products.all()), 1)

    def test_auth_add_two_diff_products(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        response = self.c.post('/add_to_cart', {'quantity': 1, 'product_id': 2, 'a': 3, 'b': 3})
        self.assertEqual(len(self.user.cart.products.all()), 2)

    def test_unauth_make_new_cart(self):
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        request = response.wsgi_request
        self.assertEqual(len(request.session['cart']), 1)

    def test_unauth_add_two_prod(self):
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        response = self.c.post('/add_to_cart', {'quantity': 1, 'product_id': 1, 'a': 2, 'b': 3})
        request = response.wsgi_request
        self.assertEqual(len(request.session['cart']), 1)

    def test_cart_from_session_to_db(self):
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        response = self.c.post('/add_to_cart', {'quantity': 2, 'product_id': 2, 'a': 3, 'b': 3})
        request = response.wsgi_request
        views.__cart_from_session_to_db__(request.session['cart'], self.user)
        self.assertEqual(len(self.user.cart.products.all()), 2)


class TestDelFromCart(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                                            price='1',
                                            main_category=self.cat1)
        self.prod2 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat2)
        self.mod1 = Modification.objects.create(product=self.prod1,
                                            characteristics="{'a': '2', 'b': '3'}")
        self.sp = StockProduct.objects.create(product=self.prod1,
                                                modification=self.mod1,
                                              quantity=5)
        self.factory = RequestFactory()


    def test_auth_del_one_prod(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        response = self.c.post('/del_from_cart', {'stock_product_id': 1})
        self.assertEqual(len(self.user.cart.products.all()), 0)


    def test_auth_del_nonexistent_prod(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        response = self.c.post('/del_from_cart', {'stock_product_id': 2})
        self.assertEqual(len(self.user.cart.products.all()), 1)


    def test_unauth_del_one_prod(self):
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        request = response.wsgi_request
        response = self.c.post('/del_from_cart', {'stock_product_id': 1})
        request = response.wsgi_request
        self.assertEqual(len(request.session['cart']), 0)


class TestMakeOrder(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                                            price='1',
                                            main_category=self.cat1)
        self.prod2 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat2)
        self.mod1 = Modification.objects.create(product=self.prod1,
                                                characteristics="{'a': '2', 'b': '3'}")
        self.mod2 = Modification.objects.create(product=self.prod2,
                                                characteristics="{'a': '3', 'b': '3'}")
        self.sp = StockProduct.objects.create(product=self.prod1,
                                              modification=self.mod1,
                                              quantity=5)
        self.sp1 = StockProduct.objects.create(product=self.prod2,
                                               modification=self.mod2,
                                               quantity=5)
        self.ad = Addresses.objects.create(city= 'city', street= 'street', building= 1, flat= 1, entrance= 1)
        self.factory = RequestFactory()


    def test_auth_make_order_1(self):
        self.c.login(username='a', password='a')
        self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        self.c.post('/add_to_cart', {'quantity': 2, 'product_id': 2, 'a': 3, 'b': 3})
        self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': 1, 'flat': 1, 'entrance': 1})
        response = self.c.post('/make_order',
                               {'address_id': 1})
        self.assertEqual(len(Order.objects.filter(author=self.user)), 1)


    def test_auth_make_order_2(self):
        self.c.login(username='a', password='a')
        self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        self.c.post('/add_to_cart', {'quantity': 2, 'product_id': 2, 'a': 3, 'b': 3})
        self.c.post('/add_address',
                               {'city': 'city', 'street': 'street', 'building': 1, 'flat': 1, 'entrance': 1})
        response = self.c.post('/make_order',
                               {'address_id': 1})
        self.assertEqual(len(Order.objects.filter(author=self.user)[0].products.all()), 2)


    def test_unauth_make_order_1(self):
        self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        self.c.post('/add_to_cart', {'quantity': 2, 'product_id': 2, 'a': 3, 'b': 3})
        self.c.post('/make_order',
                               {'email': 'lol@kek.su', 'city': 'city', 'street': 'street', 'building': 1, 'flat': 1, 'entrance': 1})
        self.assertEqual(len(Order.objects.filter(email='lol@kek.su')), 1)


class TestAdmin(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username='a', email='[removed_emai]', password='a', is_staff=True)
        self.user = User.objects.create_user('b', 'lol@kek.su', 'b')
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                                            price='1',
                                            main_category=self.cat1)
        self.prod2 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            main_category=self.cat2)
        self.mod1 = Modification.objects.create(product=self.prod1,
                                                characteristics="{'a': '2', 'b': '3'}")
        self.mod2 = Modification.objects.create(product=self.prod2,
                                                characteristics="{'a': '3', 'b': '3'}")
        self.mod3 = Modification.objects.create(product=self.prod3,
                                                characteristics="{'c': '3'}")
        self.sp = StockProduct.objects.create(product=self.prod1,
                                              modification=self.mod1,
                                              quantity=5)
        self.sp1 = StockProduct.objects.create(product=self.prod2,
                                               modification=self.mod2,
                                               quantity=5)
        self.ad = Addresses.objects.create(city= 'city', street= 'street', building= 1, flat= 1, entrance= 1)
        self.factory = RequestFactory()


    def test_admin_can_see_index(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_index(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/')
        self.assertEqual(response.status_code, 302)


    def test_admin_can_see_product(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/product_page/')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_product(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/product_page/')
        self.assertEqual(response.status_code, 302)


    def test_admin_can_see_category(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/category_page/')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_category(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/category_page/')
        self.assertEqual(response.status_code, 302)


    def test_admin_can_see_modification(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/modification_page')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_modification(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/modification_page')
        self.assertEqual(response.status_code, 302)


    def test_admin_can_see_stock_product(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/stock_products/')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_stock_product(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/stock_products/')
        self.assertEqual(response.status_code, 302)


    def test_admin_can_see_orders(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/orders_page')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_orders(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/orders_page')
        self.assertEqual(response.status_code, 302)


    def test_admin_can_see_users(self):
        self.c.login(username='a', password='a')
        response = self.c.get('/admin/user_list')
        self.assertEqual(response.status_code, 200)


    def test_user_cant_see_users(self):
        self.c.login(username='b', password='b')
        response = self.c.get('/admin/user_list')
        self.assertEqual(response.status_code, 302)


    def test_can_create_product(self):
        response = self.c.post('/form_product', {'cat[]': ['d'], 'main': 'd', 'name': 'lol', 'price': 123, 'rating': ''})
        self.assertEqual(len(Product.objects.filter(name='lol')), 1)


    def test_can_create_product_with_many_cat(self):
        response = self.c.post('/form_product', {'cat[]': ['d', 'b'], 'main': 'd', 'name': 'lol', 'price': 123, 'rating': ''})
        self.assertEqual(len(Product.objects.filter(name='lol')[0].categories.all()), 2)


    def test_can_change_exist_product(self):
        response = self.c.post('/change_exist_product', {'id': 1, 'cat[]': ['d', 'b'], 'main': 'd', 'name': 'lol', 'price': 123, 'rating': ''})
        self.assertEqual(len(Product.objects.filter(name='lol')[0].categories.all()), 2)


    def test_get_categories_names(self):
        response = self.c.post('/form_product',
                              {'cat[]': ['d', 'b'], 'main': 'd', 'name': 'lol', 'price': 123, 'rating': ''})
        response = self.c.post('/get_categories_by_id',
                               {'id': 4})
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'cat': ['b', 'd'], 'name': 'lol'}
        )


    def test_can_create_category(self):
        response = self.c.post('/form_category', {'name': 'lol', 'parent': 'b'})
        self.assertEqual(len(Category.objects.filter(name='lol')), 1)
        self.assertEqual(Category.objects.filter(name='lol')[0].parent_category.name, 'b')


    def test_can_change_category(self):
        response = self.c.post('/form_category', {'name': 'lol', 'parent': 'b'})
        response = self.c.post('/change_exist_category', {'name': 'kek', 'parent': '', 'id': 3})
        self.assertEqual(len(Category.objects.filter(name='kek')), 1)
        self.assertEqual(Category.objects.filter(name='kek')[0].parent_category, None)


    def test_canget_category_id(self):
        response = self.c.post('/get_category_by_id', {'id': 1})
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'name': 'b'}
        )


    def test_can_get_prod_id(self):
        response = self.c.post('/get_prod_by_name', {'name': 'abacaba'})
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'id': 1}
        )

    def test_have_modifications(self):
        response = self.c.post('/have_modifications', {'id': 3})
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'have': True, 'char': ['c'], 'values': [['3']]}
        )


    def test_form_stock_product(self):
        response = self.c.post('/form_stock_products', {'id': 1, 'ids[]': [1], 'qs[]': [3]})
        self.assertEqual(len(StockProduct.objects.all()), 2)
