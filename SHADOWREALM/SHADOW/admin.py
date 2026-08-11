
# Register your models here.
from django.contrib import admin
from .models import Category, Story, Comment, StoryScene


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'status',
        'created_at',
        'total_upvotes',
    )

    list_filter = (
        'status',
        'category',
        'created_at',
    )

    search_fields = (
        'title',
        'content',
        'summary',
        'author__username',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }


admin.site.register(StoryScene)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'story',
        'author',
        'created_at',
    )

    list_filter = (
        'created_at',
    )

    search_fields = (
        'body',
        'author__username',
        'story__title',
    )