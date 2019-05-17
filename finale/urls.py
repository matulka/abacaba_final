"""finale URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from core import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from finale import settings

handler500 = views.e_handler500
urlpatterns = [
    path('admin/', views.admin_page),
    path('admin/product_page/', views.product_page),
    path('admin/product_page/img', views.product_page_img),
    path('admin/product_page/add_product', views.add_product),
    path('admin/product_page/change_product', views.change_product),
    path('admin/category_page/', views.category_page),
    path('admin/category_page/add_category', views.add_category),
    path('admin/category_page/category_list', views.category_list),
    path('admin/category_page/category_list/change_category', views.change_category),
    path('admin/modification_page', views.modification_page),
    path('admin/modification_page/add_modification', views.add_modification),
    path('form_modifications', views.form_modifications),
    path('admin/find_out_prod', views.find_product),
    path('admin/stock_products/', views.stock_product_page),
    path('admin/stock_products/add_stock_product', views.add_stock_product),
    path('admin/stock_products/img', views.find_out_what_stock_product),
    path('admin/stock_products/change_img', views.stock_product_images),
    path('get_prod_by_name', views.get_product_by_name),
    path('find_prod_modifications', views.get_product_modifications),
    path('find_prod_sps', views.get_product_stock_products),
    path('admin/find_prod_for_img', views.find_prod_for_img),
    path('form_stock_products', views.form_stock_products),
    path('del_img', views.del_img),
    path('find_sp_images', views.find_sp_images),
    path('change_exist_product', views.change_exist_product),
    path('change_exist_category', views.change_exist_category),
    path('have_modifications', views.have_modifications),
    path('', views.index_page, name='home'),
    path('cart', views.cart_page),
    path('form_product', views.form_product),
    path('search', views.search),
    path('add_to_cart', views.add_to_cart),
    path('form_category', views.form_category),
    path('add_address', views.add_address),
    path('add_address_unauth', views.add_address_unauth),
    path('del_address', views.delete_address),
    path('del_from_cart', views.delete_from_cart),
    path('accounts/profile', views.profile),
    path('accounts/orders', views.profile_orders),
    path('accounts/addresses', views.profile_addresses),
    path('make_order', views.make_order),
    path('make_question', views.make_question),
    path('get_http_categories', views.return_categories_json),
    path('get_category_by_id', views.get_category_id),
    path('get_categories_by_id', views.get_categories_id),
    path('get_http_products', views.product_names_json),
    path('get_modifications', views.get_modifications_json),
    path('get_images', views.get_images_of_stock_product),
    path('products', views.browse_product),
    url('accounts/', include('django.contrib.auth.urls')),
    url(r'^sign-up/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
