from django.urls import path
from . import views


urlpatterns = [
path('', views.blog_list, name='blog_list'),
path('blog/create/', views.blog_create, name='blog_create'),
path('blog/timeline/', views.personal_timeline, name='personal_timeline'),
path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
path('blog/<slug:slug>/edit/', views.blog_update, name='blog_update'),
path('blog/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
path('blog/<slug:slug>/print/', views.blog_print, name='blog_print'),


path('words/', views.word_list, name='word_list'),
path('words/<int:pk>/', views.word_detail, name='word_detail'),
path('words/create/', views.word_create, name='word_create'),
path('words/<int:pk>/edit/', views.word_update, name='word_update'),
path('words/<int:pk>/delete/', views.word_delete, name='word_delete'),
]