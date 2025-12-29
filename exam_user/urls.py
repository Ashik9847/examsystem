from django.urls import path
from .import views

app_name = 'exam_user'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.user_login, name='login'),
    path('index/', views.index, name='index'),
    path('logout/', views.user_logout, name='logout'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('exam/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exam/<str:attempt_id>/', views.take_exam, name='take_exam'),
    path('exam/<str:attempt_id>/submit/', views.submit_exam, name='submit_exam'),
    path('search/', views.search_result, name='search_result'),
]