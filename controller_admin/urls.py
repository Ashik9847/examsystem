from django.urls import path
from . import views

app_name = 'controller_admin'

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),      # New
    path('logout/', views.admin_logout, name='admin_logout'),
    path('', views.dashboard, name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('category/add/', views.category_add, name='category_add'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('exam/add/<int:category_id>/', views.exam_add, name='exam_add'),
    path('exam/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:pk>/edit/', views.exam_edit, name='exam_edit'),
    path('exam/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('question/add/<int:exam_id>/', views.question_add, name='question_add'),
    path('question/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('question/<int:pk>/delete/', views.question_delete, name='question_delete'),
    path('attempts/', views.attempt_list, name='attempt_list'),
]