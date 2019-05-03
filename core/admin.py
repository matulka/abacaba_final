from django.contrib import admin
from core.models import Product, Category, Image, Modification, StockProduct


class ProductAdmin(admin.ModelAdmin):
    pass


class CategoryAdmin(admin.ModelAdmin):
    pass


class ImagesAdmin(admin.ModelAdmin):
    pass


class ModificationAdmin(admin.ModelAdmin):
    change_form_template = 'admin/models/model_change_list.html'


admin.site.site_header = 'Страничка администрации Abacaba'
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Image, ImagesAdmin)
admin.site.register(Modification, ModificationAdmin)
admin.site.register(StockProduct)