from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Category, Story, Comment, Notification, StoryScene, Report
from .forms import StoryForm, StorySceneForm, StorySceneFormSet


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

def trending(request):
    stories = Story.objects.filter(
        status='published'
    ).prefetch_related(
        'upvotes',
        'favorites',
        'comments'
    )

    # Calculate a simple trending score
    stories = sorted(
        stories,
        key=lambda story: (
            story.upvotes.count() * 3
            + story.favorites.count() * 2
            + story.comments.count() * 2
        ),
        reverse=True
    )

    return render(
        request,
        'trending.html',
        {
            'stories': stories
        }
    )

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

        scene_formset = StorySceneFormSet(
            request.POST,
            request.FILES,
            prefix='scenes'
        )

        if form.is_valid() and scene_formset.is_valid():

            story = form.save(commit=False)
            story.author = request.user
            story.save()

            scenes = scene_formset.save(commit=False)

            for scene in scenes:
                scene.story = story
                scene.save()

            for scene in scene_formset.deleted_objects:
                scene.delete()

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

        scene_formset = StorySceneFormSet(
            prefix='scenes'
        )

    return render(
        request,
        'create_story.html',
        {
            'form': form,
            'scene_formset': scene_formset,
        }
    )


@login_required
def edit_story(request, story_id):

    story = get_object_or_404(
        Story,
        id=story_id,
        author=request.user
    )

    if request.method == 'POST':

        form = StoryForm(
            request.POST,
            request.FILES,
            instance=story
        )

        scene_formset = StorySceneFormSet(
            request.POST,
            request.FILES,
            instance=story,
            prefix='scenes'
        )

        if form.is_valid() and scene_formset.is_valid():

            form.save()
            scene_formset.save()

            messages.success(
                request,
                "Your story has been updated successfully."
            )

            return redirect(
                'story_detail',
                slug=story.slug
            )

    else:

        form = StoryForm(instance=story)

        scene_formset = StorySceneFormSet(
            instance=story,
            prefix='scenes'
        )

    return render(
        request,
        'edit_story.html',
        {
            'form': form,
            'scene_formset': scene_formset,
            'story': story,
        }
    )

@login_required
def upvote_story(request, story_id):

    story = get_object_or_404(
        Story,
        id=story_id,
        status='published'
    )

    if story.upvotes.filter(id=request.user.id).exists():

        # Remove upvote
        story.upvotes.remove(request.user)

    else:

        # Add upvote
        story.upvotes.add(request.user)

        # Don't notify yourself
        if story.author != request.user:

            Notification.objects.create(
                recipient=story.author,
                sender=request.user,
                notification_type='upvote',
                story=story,
                message=f'@{request.user.username} upvoted your story "{story.title}".'
            )

    return redirect('story_detail', slug=story.slug)


@login_required
def add_comment(request, slug):

    story = get_object_or_404(
        Story,
        slug=slug,
        status='published'
    )

    if request.method == 'POST':

        body = request.POST.get('body', '').strip()

        # Get parent comment ID if this is a reply
        parent_id = request.POST.get('parent_id')

        if body:

            parent = None

            if parent_id:
                parent = get_object_or_404(
                    Comment,
                    id=parent_id,
                    story=story
                )

            Comment.objects.create(
                story=story,
                author=request.user,
                body=body,
                parent=parent
            )

    return redirect(
        'story_detail',
        slug=story.slug
    )


@login_required
def edit_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    # Only comment owner can edit
    if comment.author != request.user:
        return redirect(
            'story_detail',
            slug=comment.story.slug
        )

    if request.method == 'POST':

        body = request.POST.get('body', '').strip()

        if body:
            comment.body = body
            comment.save()

        return redirect(
            'story_detail',
            slug=comment.story.slug
        )

    return render(
        request,
        'edit_comment.html',
        {
            'comment': comment
        }
    )


@login_required
def delete_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    # Only comment owner can delete
    if comment.author != request.user:
        return redirect(
            'story_detail',
            slug=comment.story.slug
        )

    story_slug = comment.story.slug

    if request.method == 'POST':
        comment.delete()

    return redirect(
        'story_detail',
        slug=story_slug
    )


def story_detail(request, slug):

    story = get_object_or_404(
        Story.objects.select_related(
            'author',
            'category'
        ),
        slug=slug,
        status='published'
    )

    comments = story.comments.filter(
        parent=None
    ).select_related(
        'author'
    ).prefetch_related(
        'replies__author'
    )

    scenes = story.scenes.all()

    is_favorited = False

    if request.user.is_authenticated:
        is_favorited = story.favorites.filter(
            id=request.user.id
        ).exists()
        
    return render(
        request,
        'story_detail.html',
        {
            'story': story,
            'comments': comments,
            'scenes': scenes,
            'is_favorited': is_favorited,
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

@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        'sender',
        'story',
        'comment'
    )

    return render(
        request,
        'notifications.html',
        {
            'notifications': notifications
        }
    )


@login_required
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save(update_fields=['is_read'])

    if notification.story:
        return redirect(
            'story_detail',
            slug=notification.story.slug
        )

    if notification.comment:
        return redirect(
            'story_detail',
            slug=notification.comment.story.slug
        )

    return redirect('notifications')


@login_required
def mark_all_notifications_read(request):

    if request.method == 'POST':

        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(
            is_read=True
        )

    return redirect('notifications')

@login_required
def manage_scenes(request, story_id):

    story = get_object_or_404(
        Story,
        id=story_id,
        author=request.user
    )

    scenes = story.scenes.all().order_by('id')

    if request.method == 'POST':

        form = StorySceneForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            scene = form.save(commit=False)
            scene.story = story
            scene.save()

            messages.success(
                request,
                'Scene added successfully.'
            )

            return redirect(
                'manage_scenes',
                story_id=story.id
            )

    else:

        form = StorySceneForm()

    return render(
        request,
        'manage_scenes.html',
        {
            'story': story,
            'scenes': scenes,
            'form': form,
        }
    )


@login_required
def edit_scene(request, scene_id):

    scene = get_object_or_404(
        StoryScene.objects.select_related('story'),
        id=scene_id,
        story__author=request.user
    )

    if request.method == 'POST':

        form = StorySceneForm(
            request.POST,
            request.FILES,
            instance=scene
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Scene updated successfully.'
            )

            return redirect(
                'manage_scenes',
                story_id=scene.story.id
            )

    else:

        form = StorySceneForm(
            instance=scene
        )

    return render(
        request,
        'edit_scene.html',
        {
            'form': form,
            'scene': scene,
            'story': scene.story,
        }
    )


@login_required
def delete_scene(request, scene_id):

    scene = get_object_or_404(
        StoryScene.objects.select_related('story'),
        id=scene_id,
        story__author=request.user
    )

    story_id = scene.story.id

    if request.method == 'POST':

        scene.delete()

        messages.success(
            request,
            'Scene deleted successfully.'
        )

    return redirect(
        'manage_scenes',
        story_id=story_id
    )

def horror_reader(request, slug):
    story = get_object_or_404(
        Story.objects.select_related('author', 'category'),
        slug=slug,
        status='published',
        horror_mode=True
    )

    scenes = story.scenes.all().order_by('id')

    return render(
        request,
        'horror_reader.html',
        {
            'story': story,
            'scenes': scenes,
        }
    )

@login_required
def report_story(request, story_id):

    story = get_object_or_404(
        Story,
        id=story_id,
        status='published'
    )

    if request.method == 'POST':

        reason = request.POST.get('reason')
        description = request.POST.get('description', '').strip()

        if reason:

            Report.objects.create(
                reporter=request.user,
                story=story,
                reason=reason,
                description=description
            )

            messages.success(
                request,
                'Thank you. The story has been reported to the administrators.'
            )

    return redirect(
        'story_detail',
        slug=story.slug
    )


@login_required
def report_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id
    )

    if request.method == 'POST':

        reason = request.POST.get('reason')
        description = request.POST.get('description', '').strip()

        if reason:

            Report.objects.create(
                reporter=request.user,
                comment=comment,
                reason=reason,
                description=description
            )

            messages.success(
                request,
                'Thank you. The comment has been reported to the administrators.'
            )

    return redirect(
        'story_detail',
        slug=comment.story.slug
    )

@login_required
def delete_account(request):

    if request.method == 'POST':

        user = request.user

        # Delete the currently logged-in user's account.
        # No user ID/username comes from the URL, so another
        # user's account cannot be targeted by changing the URL.
        user.delete()

        messages.success(
            request,
            'Your ShadowRealm account has been permanently deleted.'
        )

        return redirect('home')

    return render(
        request,
        'delete_account.html'
    )