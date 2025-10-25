from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('history/', views.order_history_view, name='order_history'),
    path('payment/<int:order_id>/', views.process_payment_view, name='process_payment'),
    path('success/<int:order_id>/', views.payment_success_view, name='payment_success'),
    path('admin/', views.admin_orders_view, name='admin_orders'),
    path('admin/update-status/<int:order_id>/', views.update_order_status_view, name='update_order_status'),
    path('cancel/<int:order_id>/', views.cancel_order_view, name='cancel_order'),
]
