from django.contrib import admin
from core.models import Product, Category, Order, Addresses, OrderProduct, OrderProductInformation, StockProduct,\
    Modification, Cart, Question


class ProductAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass

class OrderAdmin(admin.ModelAdmin):
    pass

class AddressesAdmin(admin.ModelAdmin):
    pass

class OrderProductAdmin(admin.ModelAdmin):
    pass

class OrderProductInformationAdmin(admin.ModelAdmin):
    pass

class StockProductAdmin(admin.ModelAdmin):
    pass

class ModificationAdmin(admin.ModelAdmin):
    pass

class CartAdmin(admin.ModelAdmin):
    pass

class QuestionsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Addresses, AddressesAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(OrderProductInformation, OrderProductInformationAdmin)
admin.site.register(StockProduct, StockProductAdmin)
admin.site.register(Modification, ModificationAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Question, QuestionsAdmin)