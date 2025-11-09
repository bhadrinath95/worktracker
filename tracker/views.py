from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Task, Update, TaskType, LifePrinciple, Document
from .forms import TaskForm, UpdateForm, DocumentFormSet
from django.db.models import F
from django.http import Http404

def task_list(request):
    task_type_id = request.GET.get('task_type') 
    tasks = Task.objects.exclude(status='Completed')

    if task_type_id:
        tasks = tasks.filter(task_type_id=task_type_id)

    tasks = tasks.order_by(F('target_date').asc(nulls_last=True), 'updated_date', 'name')
    task_types = TaskType.objects.all()
    return render(request, 'tracker/task_list.html', {
        'tasks': tasks,
        'task_types': task_types,
        'selected_type': int(task_type_id) if task_type_id else None,
    })

def task_history(request):
    tasks = Task.objects.filter(status='Completed').order_by('-completed_date')
    return render(request, 'tracker/task_history.html', {'tasks': tasks})

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tracker/task_form.html', {'form': form})

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tracker/task_form.html', {'form': form})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tracker/task_confirm_delete.html', {'task': task})

def mark_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'Completed'
    task.completed_date = timezone.now()
    task.save()
    return redirect('task_list') 

def update_list(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    updates = task.updates.order_by('-date')

    if request.method == 'POST':
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
    else:
        form = UpdateForm()
        formset = DocumentFormSet(queryset=Document.objects.none())

    return render(request, 'tracker/update_list.html', {
        'task': task,
        'updates': updates,
        'form': form,
        'formset': formset,
    })

def update_edit(request, pk):
    update = get_object_or_404(Update, pk=pk)
    task = update.task

    if request.method == 'POST':
        form = UpdateForm(request.POST, instance=update)
        formset = DocumentFormSet(request.POST, queryset=update.documents.all())

        if form.is_valid() and formset.is_valid():
            form.save()
            # Handle document updates
            for doc_form in formset:
                if doc_form.cleaned_data:
                    if doc_form.cleaned_data.get('DELETE'):
                        if doc_form.instance.pk:
                            doc_form.instance.delete()
                    else:
                        doc = doc_form.save(commit=False)
                        doc.update = update
                        doc.save()
            return redirect('update_list', task_id=task.id)
    else:
        form = UpdateForm(instance=update)
        formset = DocumentFormSet(queryset=update.documents.all())

    return render(request, 'tracker/update_form.html', {
        'form': form,
        'formset': formset,
        'update': update,
    })


def update_delete(request, pk):
    update = get_object_or_404(Update, pk=pk)
    if request.method == 'POST':
        task_id = update.task.id
        update.delete()
        return redirect('update_list', task_id=task_id)
    return render(request, 'tracker/update_confirm_delete.html', {'update': update})

def prayer(request):
    return render(request, 'tracker/prayer.html', {})

def quotes(request):
    principles = LifePrinciple.objects.all().order_by('principle')
    return render(request, 'tracker/quotes.html', {'principles': principles})

def document_view(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    github_url = doc.github_url()

    return render(request, 'tracker/document_view.html', {
        'doc': doc,
        'github_url': github_url,
    })