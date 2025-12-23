from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home.html', views.home, name='home_html'), 
    path('menus/', views.menus, name='menus'),
    path('order/', views.order, name='order'),
    path('feedback/', views.feedback_page, name='feedback'),
    path('contact/', views.contact, name='contact'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('view_feedback/', views.view_feedback, name='view_feedback'),
    path('api/feedback/', views.get_feedback_data, name='get_feedback_data'),
    path('order_form/', views.order_form, name='order_form'),
    path('feedback_form/', views.feedback_form, name='feedback_form'),
    path('order_success/', views.order_success, name='order_success'),
    path('feedback_success/', views.feedback_success, name='feedback_success'),
    path("order_history/", views.order_history, name="order_history"),
    path('custom-admin/login/', views.admin_login, name='admin_login'),
    path('custom-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/orders/', views.admin_orders, name='admin_orders'),
    path('custom-admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('custom-admin/kds/', views.admin_kds, name='admin_kds'),
    path('custom-admin/feedback/', views.admin_feedback, name='admin_feedback'),
    path('custom-admin/logout/', views.admin_logout, name='admin_logout'),
]
