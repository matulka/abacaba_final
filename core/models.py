from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    parent_category = models.ForeignKey('self',
                                        on_delete=models.CASCADE,
                                        blank=True,
                                        null=True,
                                        related_name='child_categories')

    def __str__(self):
        return 'Категория: ' + self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    price = models.IntegerField(validators=[MinValueValidator(0)])
    rating = models.FloatField(blank=True,
                               null=True,
                               validators=[MinValueValidator(0), MaxValueValidator(5)])
    categories = models.ManyToManyField(to=Category,
                                        blank=True,
                                        related_name='products')
    main_category = models.ForeignKey(to=Category,
                                      blank=True,
                                      null=True,
                                      on_delete=models.CASCADE)

    def __str__(self):
        return 'Продукт: ' + self.name

    def __str__(self):
        return self.name


class Modification(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(to=Product,
                                on_delete=models.CASCADE,
                                related_name='modifications')
    characteristics = models.TextField()

    def __str__(self):
        return 'Модификация: ' + self.characteristics


class StockProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(to=Product,
                                on_delete=models.CASCADE,
                                related_name='stock_products')
    modification = models.OneToOneField(to=Modification,
                                        on_delete=models.CASCADE,
                                        related_name='stock_product')
    quantity = models.IntegerField()

    def __str__(self):
        return 'Складовый продукт: ' + str(self.modification)


class ProductFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.TextField(null=True)
    score = models.IntegerField(default=5)
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        null=True,
        related_name='feedbacks'
    )
    author = models.ForeignKey(to=User,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='feedbacks')


class Addresses(models.Model):
    id = models.AutoField(primary_key=True)
    customers = models.ManyToManyField(User)
    city = models.TextField(default='Москва')
    street = models.TextField(default='Довженко')
    building = models.IntegerField(default=1)
    flat = models.IntegerField(default=1)
    entrance = models.TextField(null=True, blank=True)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.TextField(default='Ожидает подтверждения')
    author = models.ForeignKey(to=User,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(to=Addresses,
                                on_delete=models.CASCADE,
                                null=True,
                                related_name='orders')
    email = models.TextField(null=True)  # #Электронная почта для заказов от незарегистрированных пользователей


class Cart(models.Model):
    author = models.OneToOneField(to=User, on_delete=models.CASCADE)


class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    stock_product = models.ForeignKey(to=StockProduct,
                                      on_delete=models.CASCADE,
                                      related_name='order_products')
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        null=True,
        related_name='products'
    )
    cart = models.ForeignKey(
        to=Cart,
        on_delete=models.CASCADE,
        null=True,
        related_name='products'
    )


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(to=User,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='questions')
    topic = models.TextField()
    content = models.TextField()
    status = models.TextField(default='Рассматривается')
    admin_login = models.TextField(null=True)



class OrderProductInformation(models.Model):
    quantity = models.IntegerField()
    stock_product = models.ForeignKey(to=StockProduct,
                                      on_delete=models.CASCADE,
                                      related_name='opi')
class Image(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images',
                              null=True)
    description = models.TextField(null=True,
                                   blank=True)
    stock_product = models.ForeignKey(to=StockProduct,
                                      on_delete=models.CASCADE,
                                      related_name='images',
                                      null=True,
                                      blank=True)
    product = models.OneToOneField(Product,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True)

    def __str__(self):
        return 'Изображение: ' + self.description


