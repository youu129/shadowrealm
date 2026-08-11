from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

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

    path(
        'story/<slug:slug>/comment/',
        views.add_comment,
        name='add_comment'
    ),

     # NEW
    path(
        'story/<int:story_id>/favorite/',
        views.favorite_story,
        name='favorite_story'
    ),

    path(
        'story/<int:story_id>/delete/',
        views.delete_story,
        name='delete_story'
    ),

    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    path(
    'notifications/',
    views.notifications,
    name='notifications'
    ),

    path(
    'trending/',
    views.trending,
    name='trending'
    ),

    path(
    'story/<int:story_id>/edit/',
    views.edit_story,
    name='edit_story'
    ),

    path(
    'comment/<int:comment_id>/edit/',
    views.edit_comment,
    name='edit_comment'
    ),

    path(
    'comment/<int:comment_id>/delete/',
    views.delete_comment,
    name='delete_comment'
    ),

    path(
    'story/<int:story_id>/scenes/',
    views.manage_scenes,
    name='manage_scenes'
    ),

    path(
    'story/<slug:slug>/horror/',
    views.horror_reader,
    name='horror_reader'
    ),

    path(
    'scene/<int:scene_id>/edit/',
    views.edit_scene,
    name='edit_scene'
    ),

    path(
    'scene/<int:scene_id>/delete/',
    views.delete_scene,
    name='delete_scene'
    ),
]