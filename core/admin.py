from django.contrib import admin
from core.models import Product, Category, Image, Modification, StockProduct, Cart, OrderProduct, Addresses, Order


class ProductAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


class ImagesAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Image, ImagesAdmin)
admin.site.register(Modification)
admin.site.register(StockProduct)
admin.site.register(Cart)
admin.site.register(OrderProduct)
admin.site.register(Addresses)
admin.site.register(Order)
