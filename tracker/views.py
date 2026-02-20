from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy, reverse
from django.db.models import F, Q
from .models import Task, Update, TaskType, LifePrinciple, Document, LifePrincipleTopic
from .forms import TaskForm, UpdateForm, DocumentFormSet, TaskFromTemplateForm, MultipleUpdateForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UpdateTemplate
from datetime import datetime
from datetime import datetime, date, timedelta
from calendar import monthrange
from django.db import transaction
from copy import copy
from django.utils.dateparse import parse_date

# -------------------------
# TASK VIEWS
# -------------------------

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tracker/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = Task.objects.exclude(
            status__in=['Completed', 'Cancelled', 'Hold']
        ).exclude(
            is_bookmark=True
        ).exclude(
            is_template=True
        )

        view_mode = self.request.GET.get('view', 'public')

        # 🔒 Private / Public Logic
        if view_mode == "private":
            user_profile = getattr(self.request.user, "userprofile", None)

            if user_profile is None or not user_profile.special_privilege_password:
                messages.error(self.request, "You do not have access to private tasks.")
                return Task.objects.none()

            if not self.request.session.get("private_access"):
                raise PermissionError("PRIVATE_ACCESS_REQUIRED")

            queryset = queryset.filter(is_private=True)

        elif view_mode == "public":
            self.request.session['private_access'] = False
            queryset = queryset.filter(is_private=False)

        # 🔍 Search filter
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(updates__description__icontains=search_query)
            ).distinct()

        # 📂 Task type filter
        task_type_id = self.request.GET.get('task_type')
        if task_type_id:
            queryset = queryset.filter(task_type_id=task_type_id)

        tasks = list(queryset)

        # Remove today's tasks from upcoming
        tasks = [t for t in tasks if t.days_till_upcoming != 0]

        # Custom sorting
        tasks.sort(
            key=lambda t: (
                t.days_till_upcoming is None,
                t.days_till_upcoming,
                t.target_date is None,
                t.target_date,
                t.name.lower(),
            )
        )

        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        task_type_id = self.request.GET.get('task_type')
        search_query = self.request.GET.get('search', '')
        view_mode = self.request.GET.get('view', 'public')

        context['task_types'] = TaskType.objects.all()
        context['selected_type'] = int(task_type_id) if task_type_id else None
        context['search_query'] = search_query
        context['view_mode'] = view_mode

        common_filters = {}

        if task_type_id:
            common_filters['task_type_id'] = task_type_id

        if search_query:
            common_filters['name__icontains'] = search_query

        # Handle private/public
        if view_mode == "private":
            common_filters['is_private'] = True

        # Base queryset
        base_queryset = Task.objects.filter(**common_filters) \
            .exclude(status__in=['Completed', 'Cancelled', 'Hold']) \
            .exclude(is_bookmark=True) \
            .exclude(is_template=True) \
            .order_by('name')

        # 🟢 Today's Tasks
        today_tasks = [
            task for task in base_queryset
            if task.days_till_upcoming == 0
        ]
        context['today_tasks'] = today_tasks

        if view_mode == "public":
            common_filters['is_private'] = False

        # 🟡 Held Tasks
        held_tasks = Task.objects.filter(
            status__in=['Hold'],
            **common_filters
        ).exclude(is_template=True).order_by('name')

        context['held_tasks'] = held_tasks

        # ⭐ Bookmarked Tasks
        bookmarked_tasks = Task.objects.filter(
            is_bookmark=True,
            status__in=['Opened', 'InProgress'],
            **common_filters
        ).exclude(is_template=True).order_by('name')

        context['bookmarked_tasks'] = bookmarked_tasks

        # 📋 Template Tasks
        template_tasks = Task.objects.filter(
            is_template=True,
            **common_filters
        ).order_by('name')

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
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(updates__description__icontains=search)
            ).distinct()

        if start_date and end_date:
            queryset = queryset.filter(
                Q(started_date__range=[start_date, end_date]) |
                Q(completed_date__range=[start_date, end_date])
            )

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
def update_filter(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')


    if not start_date or not end_date:
        updates = Update.objects.none()
    else:
        updates = (
            Update.objects
            .select_related('task')
            .filter(
                task__is_private=False,
                task__is_template=False
            )
            .order_by(F('date').asc(nulls_last=True))
        )

        if start_date:
            start_date = parse_date(start_date)
            updates = updates.filter(date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            updates = updates.filter(date__lte=end_date)

    context = {
        'updates': updates,
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
    }

    return render(request, 'tracker/update_filter.html', context)

@login_required
def toggle_hold(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = "Hold" if task.status == "Opened" else "Opened"
    task.save()
    if task.status == "Hold":
        messages.warning(request, "Task moved to Hold.")
    else:
        messages.success(request, "Task Activated.")
    return redirect('tracker:task_list')

def mark_task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.status = 'Completed'
    task.completed_date = timezone.localdate()
    task.save()
    messages.success(request, f'🎉 Congratulations! Task "{task.name}" has been marked as completed.')
    return redirect('tracker:task_list')

def mark_task_cancel(request, pk):
    task = get_object_or_404(Task, id=pk)

    if task.status not in ['Completed', 'Cancelled']:
        task.status = 'Cancelled'
        task.save()
        messages.success(request, "Task marked as Cancelled.")
    else:
        messages.warning(request, "Task is already Completed or Cancelled.")

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

        checkbox_updates_count = task.updates.filter(
            is_check_box=True
        ).exclude(
            status__in=['Completed', 'Cancelled']
        ).count()
        normal_updates_count = task.updates.filter(
            is_check_box=False
        ).exclude(
            status__in=['Completed', 'Cancelled']
        ).count()
        checkbox_updates = task.updates.filter(is_check_box=True).order_by('-status', F('date').asc(nulls_first=True), 'description')
        normal_updates   = task.updates.filter(is_check_box=False).order_by(F('date').asc(nulls_first=True),)

        form = MultipleUpdateForm()
        formset = DocumentFormSet(queryset=Document.objects.none())

        return render(request, 'tracker/update_list.html', {
            'task': task,
            'checkbox_updates': checkbox_updates,
            'updates': normal_updates,
            'checkbox_updates_count': checkbox_updates_count,
            'normal_updates_count': normal_updates_count,
            'form': form,
            'formset': formset,
        })

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        if task.is_private:
            if not self.request.session.get("private_access"):
                raise PermissionError("PRIVATE_ACCESS_REQUIRED")
        form = MultipleUpdateForm(request.POST)
        formset = DocumentFormSet(request.POST, queryset=Document.objects.none())

        if form.is_valid() and formset.is_valid():
            dates_str = form.cleaned_data.get('dates')
            if dates_str == "":
                update = Update(
                    task=task,
                    date=None,
                    description=form.cleaned_data['description'],
                    is_check_box=form.cleaned_data['is_check_box'],
                    status=form.cleaned_data['status'],
                    reminder_type=form.cleaned_data['reminder_type'],
                    date_to_remind=form.cleaned_data['date_to_remind'],
                    can_store_reminder=form.cleaned_data['can_store_reminder'],
                )
                update.save()
                for doc_form in formset:
                    if doc_form.cleaned_data and not doc_form.cleaned_data.get('DELETE', False):
                        doc = doc_form.save(commit=False)
                        doc.update = update
                        doc.save()
                return redirect('tracker:update_list', task_id=task_id)
            
            dates = [
                datetime.strptime(d, "%Y-%m-%d").date()
                for d in dates_str.split(',')
            ]
            
            updates = []

            for date in dates:
                update = Update(
                    task=task,
                    date=date,
                    description=form.cleaned_data['description'],
                    is_check_box=form.cleaned_data['is_check_box'],
                    status=form.cleaned_data['status'],
                    reminder_type=form.cleaned_data['reminder_type'],
                    date_to_remind=form.cleaned_data['date_to_remind'],
                    can_store_reminder=form.cleaned_data['can_store_reminder'],
                )
                update.save()
                updates.append(update)

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

def update_status(update, status):
    today = timezone.localdate()

    # ---- store completed copy ----
    if update.can_store_reminder:
        update_copy = copy(update)
        update_copy.pk = None
        update_copy.date = today
        update_copy.is_check_box = False
        update_copy.status = status
        update_copy.save()

    # ---- calculate next reminder date ----
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
            update.date = date(year, month, monthrange(year, month)[1])

    elif update.reminder_type == 'Yearly':
        year = update.date.year + 1
        month = update.date.month
        day = update.date_to_remind or update.date.day
        update.date_to_remind = day
        try:
            update.date = date(year, month, day)
        except ValueError:
            update.date = date(year, month, monthrange(year, month)[1])

    elif update.reminder_type == 'Weekly':
        current_weekday = (update.date.weekday() + 1) % 7
        target_weekday = update.date_to_remind
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:
            days_ahead += 7
        update.date += timedelta(days=days_ahead)

    elif update.reminder_type == 'Days':
        update.date += timedelta(days=update.date_to_remind)

    else:
        update.date = today
        update.status = status

    update.save()

class UpdateCancelledView(LoginRequiredMixin, View):
    def post(self, request, update_id):
        update = get_object_or_404(Update, pk=update_id)
        update_status(update, 'Cancelled')
        return redirect('tracker:update_list', task_id=update.task.id)

class UpdateCompleteView(LoginRequiredMixin, View):
    def post(self, request, update_id):
        update = get_object_or_404(Update, pk=update_id)
        update_status(update, 'Completed')
        return redirect('tracker:update_list', task_id=update.task.id)

class TodayTaskUpdatesCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        today = timezone.localdate()
        task = get_object_or_404(Task, pk=pk)
        updates = Update.objects.filter(
            task=task,
            date=today,
            status__in=['Opened', 'InProgress'],
        )
        if not updates.exists():
            messages.warning(
                request,
                f'No updates found for task "{task.name}" for today.'
            )
            return redirect('tracker:update_list', task_id=task.id)
        with transaction.atomic():
            for update in updates:
                update_status(update, 'Completed')
        return redirect('tracker:update_list', task_id=task.id)

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
        "preview_html": doc.render_preview(),
    })
