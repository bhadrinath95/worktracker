from django.urls import path

from .views import (
    TreeView,
    StatementCreateView,
    StatementUpdateView,
    StatementDeleteView,
    DecisionTreeListView,
    DecisionTreeCreateView,
    DecisionTreeUpdateView,
    DecisionTreeDeleteView,
)

urlpatterns = [

    path(
        "",
        DecisionTreeListView.as_view(),
        name="decision_tree_list"
    ),

    path(
        "create/",
        DecisionTreeCreateView.as_view(),
        name="decision_tree_create"
    ),

    path(
        "<int:pk>/update/",
        DecisionTreeUpdateView.as_view(),
        name="decision_tree_update"
    ),

    path(
        "<int:pk>/delete/",
        DecisionTreeDeleteView.as_view(),
        name="decision_tree_delete"
    ),

    path(
        "node/create/",
        StatementCreateView.as_view(),
        name="statement_create"
    ),

    path(
        "node/<int:pk>/update/",
        StatementUpdateView.as_view(),
        name="statement_update"
    ),

    path(
        "node/<int:pk>/delete/",
        StatementDeleteView.as_view(),
        name="statement_delete"
    ),

    path(
        "<int:tree_id>/",
        TreeView.as_view(),
        name="tree_view"
    ),
]