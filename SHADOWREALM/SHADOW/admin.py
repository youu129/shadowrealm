from django.contrib import admin

from .models import (
    Category,
    Story,
    Comment,
    StoryScene,
    Notification,
    Report,
)


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
    )

    search_fields = (
        'name',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


# =========================================================
# STORY
# =========================================================

@admin.action(description='Delete selected stories')
def delete_selected_stories(modeladmin, request, queryset):

    count = queryset.count()

    queryset.delete()

    modeladmin.message_user(
        request,
        f'{count} story/stories deleted successfully.'
    )


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

    actions = (
        delete_selected_stories,
    )


# =========================================================
# STORY SCENE
# =========================================================

@admin.register(StoryScene)
class StorySceneAdmin(admin.ModelAdmin):

    list_display = (
        'story',
        'id',
        'is_jumpscare',
        'created_at',
    )

    list_filter = (
        'is_jumpscare',
        'created_at',
    )

    search_fields = (
        'story__title',
        'text',
    )


# =========================================================
# COMMENTS
# =========================================================

@admin.action(description='Delete selected comments/replies')
def delete_selected_comments(modeladmin, request, queryset):

    count = queryset.count()

    queryset.delete()

    modeladmin.message_user(
        request,
        f'{count} comment/reply item(s) deleted successfully.'
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'story',
        'author',
        'parent',
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

    actions = (
        delete_selected_comments,
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'recipient',
        'sender',
        'notification_type',
        'is_read',
        'created_at',
    )

    list_filter = (
        'notification_type',
        'is_read',
        'created_at',
    )

    search_fields = (
        'recipient__username',
        'sender__username',
        'message',
    )


# =========================================================
# REPORTS
# =========================================================

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'reporter',
        'reported_object',
        'reason',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'reason',
        'created_at',
    )

    search_fields = (
        'reporter__username',
        'description',
        'story__title',
        'comment__body',
    )

    list_editable = (
        'status',
    )

    readonly_fields = (
        'reporter',
        'story',
        'comment',
        'reason',
        'description',
        'created_at',
    )

    def reported_object(self, obj):

        if obj.story:
            return f'Story: {obj.story.title}'

        if obj.comment:
            return f'Comment #{obj.comment.id}'

        return 'Unknown'