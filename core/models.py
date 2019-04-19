from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    parent_id = models.IntegerField(blank=True,
                                    null=True)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    price = models.IntegerField()
    rating = models.FloatField(blank=True,
                               null=True)
    category = models.ForeignKey(to=Category,
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 null=True,
                                 related_name='products')
    sample_image = models.ImageField(upload_to='images',
                                     null=True)


class Modification(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(to=Product,
                                on_delete=models.CASCADE,
                                related_name='modifications')
    characteristics = models.TextField()


class StockProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.OneToOneField(to=Product,
                                   on_delete=models.CASCADE,
                                   related_name='stock_product')
    modification = models.OneToOneField(to=Modification,
                                        on_delete=models.CASCADE,
                                        related_name='stock_product')
    image = models.ImageField(upload_to='images',
                              blank=True,
                              null=True)  # #product.image.url
    quantity = models.IntegerField()


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
    entrance = models.TextField(null=True)


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
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')


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
