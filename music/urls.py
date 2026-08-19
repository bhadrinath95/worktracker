from django.urls import path

from . import views


urlpatterns = [

    # ========================================================
    # MUSIC
    # ========================================================

    path("", views.music_list, name="music_list"),
    path("add/", views.music_create, name="music_create"),
    path("<int:pk>/edit/", views.music_update, name="music_update"),
    path("<int:pk>/delete/", views.music_delete, name="music_delete"),

    # ========================================================
    # ARTIST
    # ========================================================

    path("artists/", views.artist_list, name="artist_list"),
    path("artists/add/", views.artist_create, name="artist_create"),
    path("artists/<int:pk>/edit/", views.artist_update, name="artist_update"),
    path("artists/<int:pk>/delete/", views.artist_delete, name="artist_delete"),

    # ========================================================
    # CATEGORY
    # ========================================================

    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
]