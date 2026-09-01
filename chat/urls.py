from django.urls import path

from . import views

app_name = "chat"


urlpatterns = [
    path("", views.conversation_list, name="conversation_list"),
    path("create/", views.conversation_create, name="conversation_create",),
    path("<slug:slug>/", views.conversation_detail, name="conversation_detail"),
    path("<slug:slug>/delete/confirm/", views.conversation_delete_confirm, name="conversation_delete_confirm"),
    path("<slug:slug>/delete/", views.conversation_delete, name="conversation_delete"),
    path("<slug:slug>/update/", views.conversation_update, name="conversation_update"),
    path("<slug:slug>/chat/", views.chat_message, name="chat_message"),
]