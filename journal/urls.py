from django.urls import path
from . import views

app_name = "journal"

urlpatterns = [
    path("", views.view_topic, name="view_topic"),
    path("topics/create/", views.create_topic, name="create_topic"),
    path("topics/<int:topic_id>/edit/", views.modify_topic, name="modify_topic"),
    path("topics/<int:topic_id>/delete/", views.delete_topic, name="delete_topic"),

    path("topics/<int:topic_id>/stories/", views.view_story, name="view_story"),
    path("stories/create/", views.create_story, name="create_story"),
    path("topics/<int:topic_id>/stories/create/", views.create_story, name="create_story_for_topic"),
    path("stories/<int:story_id>/", views.detail_story, name="detail_story"),
    path("stories/<int:story_id>/edit/", views.modify_story, name="modify_story"),
    path("stories/<int:story_id>/delete/", views.delete_story, name="delete_story"),
]
