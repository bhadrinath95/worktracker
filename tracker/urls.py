from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/new/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_update, name='task_update'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:task_id>/updates/', views.update_list, name='update_list'),
    path('task/<int:pk>/complete/', views.mark_task_complete, name='mark_task_complete'),
    path('update/<int:pk>/edit/', views.update_edit, name='update_edit'),
    path('update/<int:pk>/delete/', views.update_delete, name='update_delete'),
    path('history/', views.task_history, name='task_history'),
    path('prayer/', views.prayer, name='prayer'),
    path('quotes/', views.quotes, name='quotes'),
    path('document/<int:pk>/', views.document_view, name='document_view'),
]
