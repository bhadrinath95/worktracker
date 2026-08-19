from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from .models import Music, Artist, Category
from .forms import MusicForm, ArtistForm, CategoryForm
from django.contrib.auth.decorators import login_required


# ============================================================
# MUSIC
# ============================================================

@login_required
def music_list(request):

    songs = Music.objects.select_related(
        "category"
    ).prefetch_related(
        "artists"
    )

    artists = Artist.objects.all()
    categories = Category.objects.all()

    selected_artist = request.GET.get("artist")
    selected_category = request.GET.get("category")


    # Artist filter
    if selected_artist:
        songs = songs.filter(
            artists__id=selected_artist
        ).distinct()


    # Category filter
    if selected_category:
        songs = songs.filter(
            category_id=selected_category
        )


    context = {
        "songs": songs,
        "artists": artists,
        "categories": categories,
        "selected_artist": selected_artist,
        "selected_category": selected_category,
    }

    return render(
        request,
        "music/music_list.html",
        context
    )

@login_required
def music_create(request):

    if request.method == "POST":
        form = MusicForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("music:music_list")

    else:
        form = MusicForm()

    return render(
        request,
        "music/music_form.html",
        {
            "form": form,
            "title": "Add Song",
        }
    )


@login_required
def music_update(request, pk):

    music = get_object_or_404(Music, pk=pk)

    if request.method == "POST":
        form = MusicForm(
            request.POST,
            instance=music
        )

        if form.is_valid():
            form.save()
            return redirect("music:music_list")

    else:
        form = MusicForm(instance=music)

    return render(
        request,
        "music/music_form.html",
        {
            "form": form,
            "title": "Edit Song",
            "music": music,
        }
    )


@login_required
def music_delete(request, pk):

    music = get_object_or_404(Music, pk=pk)

    if request.method == "POST":
        music.delete()
        return redirect("music:music_list")

    return render(
        request,
        "music/music_confirm_delete.html",
        {
            "music": music,
        }
    )


# ============================================================
# ARTIST
# ============================================================

@login_required
def artist_list(request):

    artists = Artist.objects.all()

    return render(
        request,
        "music/artist_list.html",
        {
            "artists": artists,
        }
    )


@login_required
def artist_create(request):

    if request.method == "POST":
        form = ArtistForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("music:artist_list")

    else:
        form = ArtistForm()

    return render(
        request,
        "music/artist_form.html",
        {
            "form": form,
            "title": "Add Artist",
        }
    )


@login_required
def artist_update(request, pk):

    artist = get_object_or_404(
        Artist,
        pk=pk
    )

    if request.method == "POST":
        form = ArtistForm(
            request.POST,
            instance=artist
        )

        if form.is_valid():
            form.save()
            return redirect("music:artist_list")

    else:
        form = ArtistForm(instance=artist)

    return render(
        request,
        "music/artist_form.html",
        {
            "form": form,
            "title": "Edit Artist",
            "artist": artist,
        }
    )


@login_required
def artist_delete(request, pk):

    artist = get_object_or_404(
        Artist,
        pk=pk
    )

    if request.method == "POST":
        artist.delete()
        return redirect("music:artist_list")

    return render(
        request,
        "music/artist_confirm_delete.html",
        {
            "artist": artist,
        }
    )


# ============================================================
# CATEGORY
# ============================================================

@login_required
def category_list(request):

    categories = Category.objects.all()

    return render(
        request,
        "music/category_list.html",
        {
            "categories": categories,
        }
    )


@login_required
def category_create(request):

    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("music:category_list")

    else:
        form = CategoryForm()

    return render(
        request,
        "music/category_form.html",
        {
            "form": form,
            "title": "Add Category",
        }
    )


@login_required
def category_update(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            instance=category
        )

        if form.is_valid():
            form.save()
            return redirect("music:category_list")

    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "music/category_form.html",
        {
            "form": form,
            "title": "Edit Category",
            "category": category,
        }
    )


@login_required
def category_delete(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":
        category.delete()
        return redirect("music:category_list")

    return render(
        request,
        "music/category_confirm_delete.html",
        {
            "category": category,
        }
    )