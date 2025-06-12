# builds/urls.py
from django.urls import path
from . import views

app_name = 'builds'

urlpatterns = [
    path('', views.build_list, name='build_list'),
    path('create/', views.build_create, name='build_create'),
    path('<int:pk>/', views.build_detail, name='build_detail'),
    path('cart/', views.cart_view, name='cart'),  # <----  Проверьте имя!
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('<int:pk>/edit/', views.build_edit, name='build_edit'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('employee/orders/', views.employee_order_list, name='employee_order_list'),
    path('employee/orders/<int:order_id>/update/', views.employee_order_update, name='employee_order_update'),
    path('employee/orders/<int:order_id>/complete/', views.employee_order_complete, name='employee_order_complete'),
    path('employee/orders/history/', views.employee_order_history, name='employee_order_history'), # Добавим URL для выдачи заказа
]  # Добавлено! # Добавлен путь для редактирования

