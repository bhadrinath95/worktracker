from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Statement
from .forms import StatementForm, StatementOptionFormSet
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

# Create your views here.
class StatementListView(LoginRequiredMixin, ListView):
    model = Statement
    template_name = "statements/statement_list.html"
    context_object_name = "statements"

    def get_queryset(self):
        user_profile  = getattr(self.request.user, "userprofile", None)
        if user_profile is None or not user_profile.special_privilege_password:
            messages.error(self.request, "You do not have access to private tasks.")
            return Statement.objects.none()
        if not self.request.session.get("private_access"):
            raise PermissionError("PRIVATE_ACCESS_REQUIRED")
        queryset = Statement.objects.all().order_by(
            'title',
            'created_at'
        )
        return queryset
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", 'statements:statement_list')
            raise

class StatementDetailView(LoginRequiredMixin, DetailView):
    model = Statement
    template_name = "statements/statement_detail.html"
    context_object_name = "statement"
    
    def get_context_data(self, **kwargs):
        if not self.request.session.get("private_access"):
            raise PermissionError("PRIVATE_ACCESS_REQUIRED")
        context = super().get_context_data(**kwargs)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", 'statements:statement_list')
            raise

class StatementCreateView(LoginRequiredMixin, CreateView):
    model = Statement
    form_class = StatementForm
    template_name = "statements/statement_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        formset = StatementOptionFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
        else:
            return self.form_invalid(form)

        return response

    def get_success_url(self):
        return reverse_lazy("statements:statement_detail", args=[self.object.id])

    def get_context_data(self, **kwargs):
        if not self.request.session.get("private_access"):
            raise PermissionError("PRIVATE_ACCESS_REQUIRED")
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = StatementOptionFormSet(self.request.POST)
        else:
            context["formset"] = StatementOptionFormSet()
        return context

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", 'statements:statement_list')
            raise
    
class StatementUpdateView(LoginRequiredMixin, UpdateView):
    model = Statement
    form_class = StatementForm
    template_name = "statements/statement_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        formset = StatementOptionFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
        else:
            return self.form_invalid(form)

        return response

    def get_success_url(self):
        return reverse_lazy("statements:statement_detail", args=[self.object.id])

    def get_context_data(self, **kwargs):
        if not self.request.session.get("private_access"):
            raise PermissionError("PRIVATE_ACCESS_REQUIRED")
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = StatementOptionFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = StatementOptionFormSet(instance=self.object)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", 'statements:statement_list')
            raise

class StatementDeleteView(LoginRequiredMixin, DeleteView):
    model = Statement
    template_name = "statements/statement_confirm_delete.html"
    success_url = reverse_lazy("statements:statement_list")

    def get_context_data(self, **kwargs):
        if not self.request.session.get("private_access"):
            raise PermissionError("PRIVATE_ACCESS_REQUIRED")
        context = super().get_context_data(**kwargs)
        return context
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", 'statements:statement_list')
            raise
