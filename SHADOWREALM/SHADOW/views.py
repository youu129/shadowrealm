# Create your views here.
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Story
from .forms import StoryForm

def home(request):
    return render(request,'index.html')

@login_required
def create_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            return redirect('story_detail', slug=story.slug)
    else:
        form = StoryForm()
    return render(request, 'stories/create_story.html', {'form': form})

@login_required
def upvote_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if story.upvotes.filter(id=request.user.id).exists():
        story.upvotes.remove(request.user)
    else:
        story.upvotes.add(request.user)
    return redirect('story_detail', slug=story.slug)

def story_detail(request, slug):
    story = get_object_or_404(
        Story,
        slug=slug,
        status='published'
    )

    return render(
        request,
        'story_detail.html',
        {'story': story}
    )