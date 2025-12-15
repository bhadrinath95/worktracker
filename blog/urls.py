from django.urls import path
from . import views


urlpatterns = [
path('', views.blog_list, name='blog_list'),
path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
path('blog/create/', views.blog_create, name='blog_create'),
path('blog/<int:pk>/edit/', views.blog_update, name='blog_update'),
path('blog/<int:pk>/delete/', views.blog_delete, name='blog_delete'),


path('words/', views.word_list, name='word_list'),
path('words/<int:pk>/', views.word_detail, name='word_detail'),
path('words/create/', views.word_create, name='word_create'),
path('words/<int:pk>/edit/', views.word_update, name='word_update'),
path('words/<int:pk>/delete/', views.word_delete, name='word_delete'),
]