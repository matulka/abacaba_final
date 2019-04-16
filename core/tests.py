from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Product, Category, Cart, OrderProduct, Order,\
    Addresses, Product, Question, StockProduct, Modification
from django.core.exceptions import ObjectDoesNotExist
from core import views


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

    def test_user_can_see_search_page(self):
        response = self.c.get('/search')
        self.assertEqual(response.status_code, 200)

    def test_user_can_see_categories_page(self):
        response = self.c.get('/categories')
        self.assertEqual(response.status_code, 200)


class TestSearch(TestCase):

    def setUp(self):
        self.c = Client()
        self.cat = Category.objects.create(name='b')
        self.prod1 = Product.objects.create(name='abacaba',
                             price='1',
                             category=self.cat)
        self.prod2 = Product.objects.create(name='c',
                             price='1',
                             category=self.cat)

    def test_no_text(self):
        response = self.c.get('/search', {'text': ''})
        self.assertEqual(len(response.context['products']), 2)

    def test_no_result_1(self):
        response = self.c.get('/search', {'text': 'ol'})
        self.assertEqual(len(response.context['products']), 0)

    def test_all_result(self):
        response = self.c.get('/search', {'text': 'c'})
        self.assertEqual(len(response.context['products']), 2)

    def test_one_result(self):
        response = self.c.get('/search', {'text': 'abac'})
        self.assertEqual(len(response.context['products']), 1)

    def test_none(self):
        response = self.c.get('/search')
        self.assertEqual(len(response.context['products']), 0)


class TestCategories(TestCase):

    def setUp(self):
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                             price='1',
                             category=self.cat1)
        self.prod2 = Product.objects.create(name='c',
                             price='1',
                             category=self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            category=self.cat2)

    def test_no_category(self):
        response = self.c.get('/categories', {'cat': 'a'})
        self.assertEqual(len(response.context['products']), 0)

    def test_found_category1(self):
        response = self.c.get('/categories', {'cat': 'b'})
        self.assertEqual(len(response.context['products']), 2)

    def test_found_category2(self):
        response = self.c.get('/categories', {'cat': 'd'})
        self.assertEqual(len(response.context['products']), 1)


class TestAddresses(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()

    def test_adding(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_address', {'city': 'city', 'street': 'street', 'building': 1, 'flat': 1, 'entrance': 1})
        self.assertEqual(len(Addresses.objects.all()), 1)


class TestAddToCart(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('a', '[removed_emai]', 'a')
        self.c = Client()
        self.cat1 = Category.objects.create(name='b')
        self.cat2 = Category.objects.create(name='d')
        self.prod1 = Product.objects.create(name='abacaba',
                                            price='1',
                                            category=self.cat1)
        self.prod2 = Product.objects.create(name='c',
                                            price='1',
                                            category=self.cat1)
        self.prod3 = Product.objects.create(name='c',
                                            price='1',
                                            category=self.cat2)
        self.mod1 = Modification.objects.create(product=self.prod1,
                                            characteristics="{'a': '2', 'b': '3'}")
        self.sp = StockProduct.objects.create(product=self.prod1,
                                                modification=self.mod1,
                                              quantity=5)

    def test_make_new_cart(self):
        self.c.login(username='a', password='a')
        response = self.c.post('/add_to_cart', {'quantity': 4, 'product_id': 1, 'a': 2, 'b': 3})
        self.assertEqual(len(self.user.cart.products.all()), 1)

