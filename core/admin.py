from django.contrib import admin
from core.models import Product, Category, Image, Modification, StockProduct, Cart, OrderProduct, Addresses, Order

class CategoryAdmin(admin.ModelAdmin):
    pass


class ImagesAdmin(admin.ModelAdmin):
    pass


class ModificationAdmin(admin.ModelAdmin):
    change_form_template = 'admin/models/model_change_list.html'


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Modification)
admin.site.register(StockProduct)
admin.site.register(Cart)
admin.site.register(OrderProduct)
admin.site.register(Addresses)
admin.site.register(Order)
