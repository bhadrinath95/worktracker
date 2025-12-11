from django.urls import path
from . import views

urlpatterns = [
    path("", views.StatementListView.as_view(), name="statement_list"),
    path("<int:pk>/", views.StatementDetailView.as_view(), name="statement_detail"),

    path("create/", views.StatementCreateView.as_view(), name="statement_create"),
    path("<int:pk>/edit/", views.StatementUpdateView.as_view(), name="statement_update"),
    path("<int:pk>/delete/", views.StatementDeleteView.as_view(), name="statement_delete"),
]
