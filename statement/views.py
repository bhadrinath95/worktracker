from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from .models import Statement, DecisionTree
from .forms import StatementForm, DecisionTreeForm


# =========================================================
# PRIVATE DECISION TREE ACCESS
# =========================================================

class PrivateDecisionTreeMixin:

    def dispatch(self, request, *args, **kwargs):

        user_profile = getattr(
            request.user,
            "userprofile",
            None
        )

        # User does not have private access privilege
        if (
            user_profile is None
            or not user_profile.special_privilege_password
        ):
            request.session["private_access"] = False

            messages.error(
                request,
                "You do not have access to Decision Trees."
            )

            return redirect("home")

        # User has the privilege but has not entered
        # the private access password/session
        if not request.session.get("private_access"):
            return redirect(
                "private_access",
                "statements:decision_tree_list"
            )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


# =========================================================
# TREE VIEW
# =========================================================

class TreeView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    TemplateView
):

    template_name = "statements/tree.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        tree = get_object_or_404(
            DecisionTree,
            pk=self.kwargs["tree_id"]
        )

        context["tree"] = tree

        context["roots"] = Statement.objects.filter(
            tree=tree,
            parent__isnull=True
        )

        return context


# =========================================================
# STATEMENT CREATE
# =========================================================

class StatementCreateView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    CreateView
):

    model = Statement
    form_class = StatementForm
    template_name = "statements/form.html"

    def get_initial(self):

        initial = super().get_initial()

        tree_id = self.request.GET.get("tree")
        parent_id = self.request.GET.get("parent")

        if parent_id:

            parent = get_object_or_404(
                Statement,
                pk=parent_id
            )

            initial["parent"] = parent.id
            initial["tree"] = parent.tree.id

        elif tree_id:

            tree = get_object_or_404(
                DecisionTree,
                pk=tree_id
            )

            initial["tree"] = tree.id

        return initial

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        tree = None

        tree_id = self.request.GET.get("tree")
        parent_id = self.request.GET.get("parent")

        if parent_id:

            tree = get_object_or_404(
                Statement,
                pk=parent_id
            ).tree

        elif tree_id:

            tree = get_object_or_404(
                DecisionTree,
                pk=tree_id
            )

        context["title"] = "Create Node"
        context["tree"] = tree

        return context

    def get_success_url(self):

        return reverse(
            "statements:tree_view",
            kwargs={
                "tree_id": self.object.tree.id
            }
        )


# =========================================================
# STATEMENT UPDATE
# =========================================================

class StatementUpdateView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    UpdateView
):

    model = Statement
    form_class = StatementForm
    template_name = "statements/form.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Update Node"
        context["tree"] = self.object.tree

        return context

    def get_success_url(self):

        return reverse(
            "statements:tree_view",
            kwargs={
                "tree_id": self.object.tree.id
            }
        )


# =========================================================
# STATEMENT DELETE
# =========================================================

class StatementDeleteView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    DeleteView
):

    model = Statement
    template_name = "statements/delete.html"

    def get_success_url(self):

        return reverse(
            "statements:tree_view",
            kwargs={
                "tree_id": self.object.tree.id
            }
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["statement"] = self.object
        context["tree_id"] = self.object.tree.id

        return context


# =========================================================
# DECISION TREE LIST
# =========================================================

class DecisionTreeListView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    ListView
):

    model = DecisionTree
    template_name = "statements/decision_tree_list.html"
    context_object_name = "trees"

    def get_queryset(self):

        queryset = DecisionTree.objects.all()

        search_query = self.request.GET.get(
            "search"
        )

        if search_query:

            queryset = queryset.filter(
                name__icontains=search_query
            )

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["search_query"] = self.request.GET.get(
            "search",
            ""
        )

        return context


# =========================================================
# DECISION TREE CREATE
# =========================================================

class DecisionTreeCreateView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    CreateView
):

    model = DecisionTree
    form_class = DecisionTreeForm
    template_name = "statements/decision_tree_form.html"

    success_url = reverse_lazy(
        "statements:decision_tree_list"
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Create Decision Tree"

        return context


# =========================================================
# DECISION TREE UPDATE
# =========================================================

class DecisionTreeUpdateView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    UpdateView
):

    model = DecisionTree
    form_class = DecisionTreeForm
    template_name = "statements/decision_tree_form.html"

    success_url = reverse_lazy(
        "statements:decision_tree_list"
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Update Decision Tree"

        return context


# =========================================================
# DECISION TREE DELETE
# =========================================================

class DecisionTreeDeleteView(
    LoginRequiredMixin,
    PrivateDecisionTreeMixin,
    DeleteView
):

    model = DecisionTree
    template_name = "statements/decision_tree_delete.html"

    success_url = reverse_lazy(
        "statements:decision_tree_list"
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["tree"] = self.object

        return context