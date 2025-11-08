from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Task, Update
from .forms import TaskForm, UpdateForm
from django.db.models import F

def task_list(request):
    tasks = Task.objects.exclude(status='Completed').order_by(F('target_date').asc(nulls_last=True), 'updated_date', 'name')
    return render(request, 'tracker/task_list.html', {'tasks': tasks})

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
        if form.is_valid():
            update = form.save(commit=False)
            update.task = task
            update.save()
            return redirect('update_list', task_id=task_id)
    else:
        form = UpdateForm()
    return render(request, 'tracker/update_list.html', {'task': task, 'updates': updates, 'form': form})

def update_edit(request, pk):
    update = get_object_or_404(Update, pk=pk)
    if request.method == 'POST':
        form = UpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            return redirect('update_list', task_id=update.task.id)
    else:
        form = UpdateForm(instance=update)
    return render(request, 'tracker/update_form.html', {'form': form, 'update': update})


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
    return render(request, 'tracker/quotes.html', {})