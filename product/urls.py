from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('products/', views.customer_product_list_view, name='product_list'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('admin-products/', views.product_list_view, name='admin_product_list'),
    path('add-product/', views.add_product_view, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product_view, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product_view, name='delete_product'),
    path('add-category/', views.add_category_view, name='add_category'),
    path('add-brand/', views.add_brand_view, name='add_brand'),
    path('manage-images/<int:product_id>/', views.manage_product_images_view, name='manage_images'),
    path('delete-image/<int:image_id>/', views.delete_image_view, name='delete_image'),
    path('set-primary-image/<int:image_id>/', views.set_primary_image_view, name='set_primary_image'),
]
