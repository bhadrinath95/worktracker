from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task_list'),
    path('history/', views.TaskHistoryView.as_view(), name='task_history'),
    path('task/add/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/tasktemplate/', views.TaskFromTemplateCreateView.as_view(), name='task_from_template'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('task/<int:pk>/complete/', views.mark_task_complete, name='mark_task_complete'),
    path('task/<int:pk>/toggle_hold/', views.TodayTaskUpdatesCompleteView.as_view(), name='complete_today_task_updates'),
    path('task/<int:pk>/complete_today/', views.toggle_hold, name='toggle_hold'),
    path('task/<int:task_id>/updates/', views.UpdateListView.as_view(), name='update_list'),
    path('update/<int:pk>/edit/', views.UpdateEditView.as_view(), name='update_edit'),
    path('update/<int:pk>/delete/', views.UpdateDeleteView.as_view(), name='update_delete'),
    path('update/<int:update_id>/complete/', views.UpdateCompleteView.as_view(), name='update_complete'),

    path('prayer/', views.prayer, name='prayer'),
    path('quotes/', views.quotes, name='quotes'),
    path('document/<int:pk>/', views.document_view, name='document_view'),

    path('template/<int:template_id>/description/', views.get_template_description, name='template_description'),

]
