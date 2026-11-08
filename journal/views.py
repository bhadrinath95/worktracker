from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import StoryForm, TopicForm
from .models import Story, Topic
from .rendering import render_story_markdown


@login_required
def view_topic(request):
    topics = Topic.objects.all().prefetch_related("stories")
    return render(request, "journal/topic_list.html", {"topics": topics})


@login_required
def create_topic(request):
    form = TopicForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        topic = form.save()
        messages.success(request, "Topic created successfully.")
        return redirect("journal:view_story", topic_id=topic.pk)
    return render(request, "journal/topic_form.html", {
        "form": form, "page_title": "Create Topic",
    })


@login_required
def modify_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    form = TopicForm(request.POST or None, instance=topic)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Topic updated successfully.")
        return redirect("journal:view_topic")
    return render(request, "journal/topic_form.html", {
        "form": form, "page_title": "Modify Topic", "topic": topic,
    })


@login_required
@require_POST
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.delete()  # Related stories are deleted through CASCADE.
    messages.success(request, "Topic and its stories deleted.")
    return redirect("journal:view_topic")


@login_required
def view_story(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    stories = topic.stories.all()
    return render(request, "journal/story_list.html", {
        "topic": topic, "stories": stories,
    })


@login_required
def create_story(request, topic_id=None):
    initial = {}
    if topic_id is not None:
        initial["topic"] = get_object_or_404(Topic, pk=topic_id)
    form = StoryForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        story = form.save()
        messages.success(request, "Story created successfully.")
        return redirect("journal:detail_story", story_id=story.pk)
    return render(request, "journal/story_form.html", {
        "form": form, "page_title": "Create Story",
    })


@login_required
def modify_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    form = StoryForm(request.POST or None, instance=story)
    if request.method == "POST" and form.is_valid():
        story = form.save()
        messages.success(request, "Story updated successfully.")
        return redirect("journal:detail_story", story_id=story.pk)
    return render(request, "journal/story_form.html", {
        "form": form, "page_title": "Modify Story", "story": story,
    })


@login_required
@require_POST
def delete_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    topic_id = story.topic_id
    story.delete()
    messages.success(request, "Story deleted successfully.")
    return redirect("journal:view_story", topic_id=topic_id)


@login_required
def detail_story(request, story_id):
    story = get_object_or_404(Story.objects.select_related("topic"), pk=story_id)
    return render(request, "journal/story_detail.html", {
        "story": story,
        "rendered_description": render_story_markdown(story.description),
    })
