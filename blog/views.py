from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog, Word, Tag
from .forms import BlogForm, WordForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login

@login_required
def blog_list(request):
    query = request.GET.get('q', '')
    blogs = Blog.objects.filter(personal=False)
    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    blogs = blogs.order_by('-pin', 'title', '-created_at')
    return render(request, 'blog/blog_list.html', {'blogs': blogs, 'query': query})

@login_required
def personal_timeline(request):
    query = request.GET.get('q', '')

    blogs = Blog.objects.filter(personal=True)

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    blogs = blogs.order_by('-created_at')

    return render(request, 'blog/personal_timeline.html', {
        'blogs': blogs,
        'query': query
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    if not blog.public and not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    return render(request, 'blog/blog_detail.html', {'blog': blog})

@login_required
def blog_print(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog/blog_print.html', {'blog': blog})

@login_required
def blog_create(request):
    form = BlogForm(request.POST or None)
    tags = Tag.objects.all().order_by('name')
    if form.is_valid():
        form.save()
        return redirect('blogs:blog_list')
    return render(request, 'blog/blog_form.html', {'form': form, 'tags': tags})

@login_required
def blog_update(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    tags = Tag.objects.all().order_by('name')
    form = BlogForm(request.POST or None, instance=blog)

    if form.is_valid():
        updated_blog = form.save()
        return redirect('blogs:blog_detail', slug=updated_blog.slug)

    return render(request, 'blog/blog_form.html', {
        'form': form,
        'tags': tags
    })

@login_required
def blog_delete(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if request.method == "POST":
        blog.delete()
        return redirect('blogs:blog_list')

    return render(request, 'blog/blog_confirm_delete.html', {'blog': blog})

@login_required
def word_list(request):
    query = request.GET.get('q', '')
    word_objects = Word.objects.all()
    if query:
        word_objects = word_objects.filter(
            Q(word__icontains=query) |
            Q(meaning__icontains=query) |
            Q(example__icontains=query)
        )
    word_objects = word_objects.order_by('word', '-created_at')

    words = word_objects.filter(is_phase=False)
    phases = word_objects.filter(is_phase=True)
    return render(request, 'blog/word_list.html', {'words': words, 'phases': phases, 'query': query})

@login_required
def word_detail(request, pk):
    word = get_object_or_404(Word, pk=pk)
    return render(request, 'blog/word_detail.html', {'word': word})

@login_required
def word_create(request):
    form = WordForm(request.POST or None)
    tags = Tag.objects.all()
    if form.is_valid():
        form.save()
        return redirect('blogs:word_list')
    return render(request, 'blog/word_form.html', {'form': form})

@login_required
def word_update(request, pk):
    word = get_object_or_404(Word, pk=pk)
    tags = Tag.objects.all()
    form = WordForm(request.POST or None, instance=word)
    if form.is_valid():
        form.save()
        return redirect('blogs:word_list')
    return render(request, 'blog/word_form.html', {'form': form})

@login_required
def word_delete(request, pk):
    word = get_object_or_404(Word, pk=pk)
    word.delete()
    return redirect('blogs:word_list')