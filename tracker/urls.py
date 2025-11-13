from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('history/', views.TaskHistoryView.as_view(), name='task_history'),
    path('task/add/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('task/<int:pk>/complete/', views.mark_task_complete, name='mark_task_complete'),

    path('task/<int:task_id>/updates/', views.UpdateListView.as_view(), name='update_list'),
    path('update/<int:pk>/edit/', views.UpdateEditView.as_view(), name='update_edit'),
    path('update/<int:pk>/delete/', views.UpdateDeleteView.as_view(), name='update_delete'),

    path('prayer/', views.prayer, name='prayer'),
    path('quotes/', views.quotes, name='quotes'),
    path('document/<int:pk>/', views.document_view, name='document_view'),
]
