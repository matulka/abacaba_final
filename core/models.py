from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.TextField(primary_key=True)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    price = models.IntegerField()
    information = models.TextField()
    rating = models.FloatField(null=True)
    image = models.ImageField(upload_to='images', blank=True) # #product.image.url
    category = models.ForeignKey(to=Category,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 related_name='products')


class ProductFeedback(models.Model):
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
    address = models.TextField()


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.TextField(default = 'Ожидает подтверждения')
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
    size = models.IntegerField()
    quantity = models.IntegerField()
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        null=True,
        related_name='orders'
    )
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
    admin_login = models.TextField(null=True)

