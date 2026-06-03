from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.decision_tree_list,
        name="decision_tree_list"
    ),

    path(
        "create/",
        views.decision_tree_create,
        name="decision_tree_create"
    ),

    path(
        "<int:pk>/update/",
        views.decision_tree_update,
        name="decision_tree_update"
    ),

    path(
        "<int:pk>/delete/",
        views.decision_tree_delete,
        name="decision_tree_delete"
    ),

    path(
        "node/create/",
        views.statement_create,
        name="statement_create"
    ),

    path(
        "node/<int:pk>/update/",
        views.statement_update,
        name="statement_update"
    ),

    path(
        "node/<int:pk>/delete/",
        views.statement_delete,
        name="statement_delete"
    ),

    path(
        "<int:tree_id>/",
        views.tree_view,
        name="tree_view"
    ),
]