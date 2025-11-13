from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.db.models import F
from .models import Task, Update, TaskType, LifePrinciple, Document
from .forms import TaskForm, UpdateForm, DocumentFormSet
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


# -------------------------
# TASK VIEWS
# -------------------------

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tracker/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.exclude(status='Completed')
        task_type_id = self.request.GET.get('task_type')
        if task_type_id:
            queryset = queryset.filter(task_type_id=task_type_id)
        return queryset.order_by(F('target_date').asc(nulls_last=True), 'updated_date', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        task_type_id = self.request.GET.get('task_type')
        context['task_types'] = TaskType.objects.all()
        context['selected_type'] = int(task_type_id) if task_type_id else None

        # Add today's tasks separately
        today = timezone.localdate()
        today_tasks = Task.objects.filter(
            target_date=today
        ).exclude(status='Completed')

        if task_type_id:
            today_tasks = today_tasks.filter(task_type_id=task_type_id)

        context['today_tasks'] = today_tasks.order_by('name')

        return context


class TaskHistoryView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tracker/task_history.html'
    context_object_name = 'tasks'
    queryset = Task.objects.filter(status='Completed').order_by('-completed_date')


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tracker/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tracker/task_form.html'
    success_url = reverse_lazy('task_list')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tracker/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')


def mark_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'Completed'
    task.completed_date = timezone.now()
    task.save()
    messages.success(request, f'🎉 Congratulations! Task "{task.name}" has been marked as completed.')
    return redirect('task_list')


# -------------------------
# UPDATE VIEWS
# -------------------------

class UpdateListView(LoginRequiredMixin, View):
    def get(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        updates = task.updates.order_by('-date')
        form = UpdateForm()
        formset = DocumentFormSet(queryset=Document.objects.none())
        return render(request, 'tracker/update_list.html', {
            'task': task,
            'updates': updates,
            'form': form,
            'formset': formset,
        })

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        form = UpdateForm(request.POST)
        formset = DocumentFormSet(request.POST, queryset=Document.objects.none())

        if form.is_valid() and formset.is_valid():
            update = form.save(commit=False)
            update.task = task
            update.save()

            for doc_form in formset:
                if doc_form.cleaned_data and not doc_form.cleaned_data.get('DELETE', False):
                    doc = doc_form.save(commit=False)
                    doc.update = update
                    doc.save()
            return redirect('update_list', task_id=task_id)

        updates = task.updates.order_by('-date')
        return render(request, 'tracker/update_list.html', {
            'task': task,
            'updates': updates,
            'form': form,
            'formset': formset,
        })


class UpdateEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        update = get_object_or_404(Update, pk=pk)
        form = UpdateForm(instance=update)
        formset = DocumentFormSet(queryset=update.documents.all())
        return render(request, 'tracker/update_form.html', {
            'form': form,
            'formset': formset,
            'update': update,
        })

    def post(self, request, pk):
        update = get_object_or_404(Update, pk=pk)
        form = UpdateForm(request.POST, instance=update)
        formset = DocumentFormSet(request.POST, queryset=update.documents.all())

        if form.is_valid() and formset.is_valid():
            form.save()
            for doc_form in formset:
                if doc_form.cleaned_data:
                    if doc_form.cleaned_data.get('DELETE') and doc_form.instance.pk:
                        doc_form.instance.delete()
                    else:
                        doc = doc_form.save(commit=False)
                        doc.update = update
                        doc.save()
            return redirect('update_list', task_id=update.task.id)

        return render(request, 'tracker/update_form.html', {
            'form': form,
            'formset': formset,
            'update': update,
        })


class UpdateDeleteView(LoginRequiredMixin, DeleteView):
    model = Update
    template_name = 'tracker/update_confirm_delete.html'

    def get_success_url(self):
        return reverse('update_list', kwargs={'task_id': self.object.task.id})


# -------------------------
# OTHER STATIC VIEWS
# -------------------------

@login_required(login_url='login')
def prayer(request):
    return render(request, 'tracker/prayer.html')

@login_required(login_url='login')
def quotes(request):
    principles = LifePrinciple.objects.all().order_by('principle')
    return render(request, 'tracker/quotes.html', {'principles': principles})

@login_required(login_url='login')
def document_view(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'tracker/document_view.html', {
        'doc': doc,
        'github_url': doc.github_url(),
    })
