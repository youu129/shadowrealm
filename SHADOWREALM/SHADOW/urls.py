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
]