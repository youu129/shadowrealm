from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path(
        'story/create/',
        views.create_story,
        name='create_story'
    ),

    path(
        'story/<slug:slug>/',
        views.story_detail,
        name='story_detail'
    ),

    path(
        'story/<int:story_id>/upvote/',
        views.upvote_story,
        name='upvote_story'
    ),
]