from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Statement
from .forms import StatementForm, StatementOptionFormSet
from django.shortcuts import redirect

# Create your views here.
class StatementListView(ListView):
    model = Statement
    template_name = "statements/statement_list.html"
    context_object_name = "statements"

class StatementDetailView(DetailView):
    model = Statement
    template_name = "statements/statement_detail.html"
    context_object_name = "statement"

class StatementCreateView(CreateView):
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
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = StatementOptionFormSet(self.request.POST)
        else:
            context["formset"] = StatementOptionFormSet()
        return context
    
class StatementUpdateView(UpdateView):
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
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = StatementOptionFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = StatementOptionFormSet(instance=self.object)
        return context

class StatementDeleteView(DeleteView):
    model = Statement
    template_name = "statements/statement_confirm_delete.html"
    success_url = reverse_lazy("statements:statement_list")