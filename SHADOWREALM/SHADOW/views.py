from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category, Story, Comment
from .forms import StoryForm


def home(request):
    stories = Story.objects.filter(status='published')
    categories = Category.objects.all()

    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        stories = stories.filter(
            title__icontains=query
        ) | stories.filter(
            author__username__icontains=query
        )

    if category:
        stories = stories.filter(category__slug=category)

    return render(request, 'index.html', {
        'stories': stories,
        'categories': categories,
    })

def register_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.success(
            request,
            f'Welcome to ShadowRealm, {user.username}!'
        )

        return redirect('home')

    return render(request, 'register.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                f'Welcome back, {user.username}!'
            )

            return redirect('home')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(request, 'login.html')


def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out.'
    )

    return redirect('home')

@login_required
def create_story(request):

    if request.method == 'POST':

        form = StoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            story = form.save(commit=False)

            # The logged-in user automatically becomes the author
            story.author = request.user

            story.save()

            messages.success(
                request,
                'Your story has been published!'
            )

            return redirect(
                'story_detail',
                slug=story.slug
            )

    else:
        form = StoryForm()

    return render(
        request,
        'create_story.html',
        {'form': form}
    )


@login_required
def upvote_story(request, story_id):

    story = get_object_or_404(
        Story,
        id=story_id,
        status='published'
    )

    if story.upvotes.filter(
        id=request.user.id
    ).exists():

        story.upvotes.remove(request.user)

    else:

        story.upvotes.add(request.user)

    return redirect('home')

@login_required
def add_comment(request, slug):
    story = get_object_or_404(
        Story,
        slug=slug,
        status='published'
    )

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()

        if body:
            Comment.objects.create(
                story=story,
                author=request.user,
                body=body
            )

    return redirect('story_detail', slug=story.slug)


def story_detail(request, slug):

    story = get_object_or_404(
        Story.objects.select_related(
            'author',
            'category'
        ),
        slug=slug,
        status='published'
    )

    comments = story.comments.select_related(
        'author'
    ).filter(
        parent=None
    )

    return render(
        request,
        'story_detail.html',
        {
            'story': story,
            'comments': comments
        }
    )

@login_required
def favorite_story(request, story_id):
    story = get_object_or_404(
        Story,
        id=story_id,
        status='published'
    )

    if story.favorites.filter(id=request.user.id).exists():
        story.favorites.remove(request.user)
    else:
        story.favorites.add(request.user)

    return redirect('story_detail', slug=story.slug)

@login_required
def delete_story(request, story_id):
    story = get_object_or_404(
        Story,
        id=story_id
    )

    # IMPORTANT:
    # Only the author can delete their own story.
    if story.author != request.user:
        return redirect('story_detail', slug=story.slug)

    if request.method == 'POST':
        story.delete()
        return redirect('profile')

    return render(
        request,
        'delete_story.html',
        {'story': story}
    )

@login_required
def profile(request):
    my_stories = Story.objects.filter(
        author=request.user
    )

    favorite_stories = request.user.favorite_stories.filter(
        status='published'
    )

    return render(
        request,
        'profile.html',
        {
            'my_stories': my_stories,
            'favorite_stories': favorite_stories,
        }
    )