from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy, reverse
from django.db.models import F, Q
from .models import Task, Update, TaskType, LifePrinciple, Document, LifePrincipleTopic
from .forms import TaskForm, UpdateForm, DocumentFormSet, TaskFromTemplateForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UpdateTemplate
from datetime import date, timedelta
from calendar import monthrange
from django.db import transaction

# -------------------------
# TASK VIEWS
# -------------------------

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tracker/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.exclude(status__in=['Completed', 'Cancelled', 'Hold']).exclude(is_bookmark=True).exclude(is_template=True)
        view_mode = self.request.GET.get('view', 'public')
        if view_mode == "private":
            user_profile  = getattr(self.request.user, "userprofile", None)
            if user_profile is None or not user_profile.special_privilege_password:
                messages.error(self.request, "You do not have access to private tasks.")
                return Task.objects.none()
            if not self.request.session.get("private_access"):
                raise PermissionError("PRIVATE_ACCESS_REQUIRED")
            queryset = queryset.filter(is_private=True)
        elif view_mode == "public":
            self.request.session['private_access'] = False
            queryset = queryset.filter(is_private=False)

        task_type_id = self.request.GET.get('task_type')
        if task_type_id:
            queryset = queryset.filter(task_type_id=task_type_id)

        return queryset.order_by(
            F('target_date').asc(nulls_last=True),
            'updated_date',
            'name'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        task_type_id = self.request.GET.get('task_type')
        context['task_types'] = TaskType.objects.all()
        context['selected_type'] = int(task_type_id) if task_type_id else None

        view_mode = self.request.GET.get('view', 'public')
        context['view_mode'] = view_mode

        today = timezone.localdate()

        common_filters = {}

        if view_mode == "public":
            common_filters['is_private'] = False
        elif view_mode == "private":
            common_filters['is_private'] = True

        if task_type_id:
            common_filters['task_type_id'] = task_type_id

        tasks_by_target_date = Task.objects.filter(
            started_date=today,
            target_date=today,
            **common_filters
        ).exclude(status__in=['Completed', 'Cancelled', 'Hold']).exclude(is_bookmark=True).exclude(is_template=True)
        tasks_by_updates = Task.objects.filter(
            updates__date=today,
            updates__status__in=['Opened', 'InProgress'],
            **common_filters
        ).exclude(status__in=['Completed', 'Cancelled', 'Hold']).exclude(is_bookmark=True).exclude(is_template=True)
        today_tasks = tasks_by_target_date.union(tasks_by_updates).order_by('name')
        context['today_tasks'] = today_tasks

        held_tasks = Task.objects.filter(
            status__in=['Hold'],
            **common_filters
        ).exclude(is_template=True).order_by('name')

        context['held_tasks'] = held_tasks

        bookmarked_tasks = Task.objects.filter(
            is_bookmark=True,
            status__in=['Opened', 'InProgress'],
            **common_filters
        ).exclude(is_template=True).order_by('name')

        context['bookmarked_tasks'] = bookmarked_tasks

        template_tasks = Task.objects.filter(is_template=True)
        context['template_tasks'] = template_tasks
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", "tracker:task_list") 
            raise

class TaskFromTemplateCreateView(LoginRequiredMixin, FormView):
    template_name = 'tracker/task_form.html'
    form_class = TaskFromTemplateForm
    success_url = reverse_lazy('tracker:task_list')

    def form_valid(self, form):
        template_task = form.cleaned_data['template']

        with transaction.atomic():
            # Create new Task
            new_task = Task.objects.create(
                name=form.cleaned_data['name'],
                task_type=template_task.task_type,
                started_date=form.cleaned_data.get('started_date'),
                target_date=form.cleaned_data.get('target_date'),
                status='Opened',
                is_template=False,
                is_bookmark=template_task.is_bookmark,
                is_private=template_task.is_private,
                is_important=template_task.is_important
            )

            # Clone Updates
            updates = template_task.updates.all()
            Update.objects.bulk_create([
                Update(
                    task=new_task,
                    description=upd.description,
                    date=upd.date,
                    is_check_box=upd.is_check_box,
                    status='Opened',
                    reminder_type=upd.reminder_type,
                    date_to_remind=upd.date_to_remind
                )
                for upd in updates
            ])

        return super().form_valid(form)
    
class TaskHistoryView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tracker/task_history.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.filter(status__in=['Completed', 'Cancelled']).exclude(is_template=True).order_by('-completed_date')
        search = self.request.GET.get('search', '').strip()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(updates__description__icontains=search)
            ).distinct()

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'tracker/task_history_rows.html', context)
        return super().render_to_response(context, **response_kwargs)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tracker/task_form.html'
    success_url = reverse_lazy('tracker:task_list')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tracker/task_form.html'
    success_url = reverse_lazy('tracker:task_list')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tracker/task_confirm_delete.html'
    success_url = reverse_lazy('tracker:task_list')

@login_required
def toggle_hold(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = "Hold" if task.status == "Opened" else "Hold"
    task.save()
    if task.status == "Hold":
        messages.warning(request, "Task moved to Hold.")
    else:
        messages.success(request, "Task Activated.")
    return redirect('tracker:task_list')

def mark_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'Completed'
    task.completed_date = timezone.now()
    task.save()
    messages.success(request, f'🎉 Congratulations! Task "{task.name}" has been marked as completed.')
    return redirect('tracker:task_list')


# -------------------------
# UPDATE VIEWS
# -------------------------

def get_template_description(request, template_id):
    template = get_object_or_404(UpdateTemplate, pk=template_id)
    return JsonResponse({'description': template.description})

class UpdateListView(LoginRequiredMixin, View):
    def get(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        if task.is_private:
            if not self.request.session.get("private_access"):
                raise PermissionError("PRIVATE_ACCESS_REQUIRED")

        checkbox_updates = task.updates.filter(is_check_box=True).order_by('-status', F('date').asc(nulls_first=True), 'description')
        normal_updates   = task.updates.filter(is_check_box=False).order_by(F('date').asc(nulls_first=True),)

        form = UpdateForm()
        formset = DocumentFormSet(queryset=Document.objects.none())

        return render(request, 'tracker/update_list.html', {
            'task': task,
            'checkbox_updates': checkbox_updates,
            'updates': normal_updates,
            'form': form,
            'formset': formset,
        })

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        if task.is_private:
            if not self.request.session.get("private_access"):
                raise PermissionError("PRIVATE_ACCESS_REQUIRED")
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
            return redirect('tracker:update_list', task_id=task_id)

        updates = task.updates.order_by('-date')
        return render(request, 'tracker/update_list.html', {
            'task': task,
            'updates': updates,
            'form': form,
            'formset': formset,
        })
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError as e:
            if str(e) == "PRIVATE_ACCESS_REQUIRED":
                return redirect("private_access", "tracker:task_list") 
            raise

class UpdateCompleteView(LoginRequiredMixin, View):
    def post(self, request, update_id):
        update = get_object_or_404(Update, pk=update_id)
        if update.reminder_type == 'Monthly':
            year = update.date.year
            month = update.date.month + 1
            if month == 13:
                month = 1
                year += 1
            day = update.date_to_remind
            try:
                update.date = date(year, month, day)
            except ValueError:
                last_day = monthrange(year, month)[1]
                update.date = date(year, month, last_day)
        elif update.reminder_type == 'Yearly':
            year = update.date.year + 1
            month = update.date.month
            day = update.date.day
            if update.date_to_remind:
                day = update.date_to_remind
            else:
                update.date_to_remind = day
            try:
                update.date = date(year, month, day)
            except ValueError:
                last_day = monthrange(year, month)[1]
                update.date = date(year, month, last_day)
        elif update.reminder_type == 'Weekly':
            current_date = update.date
            python_weekday = current_date.weekday()
            current_weekday = (python_weekday + 1) % 7
            target_weekday = update.date_to_remind 
            days_ahead = target_weekday - current_weekday
            if days_ahead <= 0:
                days_ahead += 7
            update.date = current_date + timedelta(days=days_ahead)
        elif update.reminder_type == 'Days':
            update.date = update.date + timedelta(days=update.date_to_remind)
        else:
            update.date = timezone.now().date()
            update.status = 'Completed'
        update.save()
        return redirect('tracker:update_list', task_id=update.task.id)

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
            return redirect('tracker:update_list', task_id=update.task.id)

        return render(request, 'tracker/update_form.html', {
            'form': form,
            'formset': formset,
            'update': update,
        })


class UpdateDeleteView(LoginRequiredMixin, DeleteView):
    model = Update
    template_name = 'tracker/update_confirm_delete.html'

    def get_success_url(self):
        return reverse('tracker:update_list', kwargs={'task_id': self.object.task.id})


# -------------------------
# OTHER STATIC VIEWS
# -------------------------

@login_required(login_url='login')
def prayer(request):
    return render(request, 'tracker/prayer.html')

@login_required(login_url='login')
def quotes(request):
    topics = LifePrincipleTopic.objects.prefetch_related(
        "principle_topic"
    ).all().order_by("topic") 

    for topic in topics:
        topic.sorted_principles = topic.principle_topic.all().order_by("principle")

    return render(request, "tracker/quotes.html", {
        "topics": topics
    })

@login_required(login_url='login')
def document_view(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'tracker/document_view.html', {
        'doc': doc,
        'github_url': doc.github_url(),
    })
