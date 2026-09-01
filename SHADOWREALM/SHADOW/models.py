from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Story(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='stories')
    cover_image = models.ImageField(upload_to='story_covers/', blank=True, null=True)
    content = models.TextField(help_text="Main text of the horror story.")
    summary = models.CharField(max_length=300, help_text="Short teaser for card previews.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    horror_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes = models.ManyToManyField(User, related_name='upvoted_stories', blank=True)
     # NEW
    favorites = models.ManyToManyField(User,related_name='favorite_stories',blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 2

            while Story.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def total_upvotes(self):
        return self.upvotes.count()

    def total_favorites(self):
        return self.favorites.count()

    def __str__(self):
        return self.title


class StoryScene(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='scenes'
    )

    text = models.TextField()

    image = models.ImageField(
        upload_to='story_scenes/',
        blank=True,
        null=True
    )

    audio = models.FileField(
        upload_to='story_scene_audio/',
        blank=True,
        null=True
    )

    is_jumpscare = models.BooleanField(default=False)

    jumpscare_image = models.ImageField(
        upload_to='jumpscares/',
        blank=True,
        null=True
    )

    jumpscare_audio = models.FileField(
        upload_to='jumpscare_audio/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.story.title} - Scene {self.id}"
    
    
class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
    'self',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='replies'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.story.title}"

#Notification
class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )

    notification_type = models.CharField(max_length=50)

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.notification_type}"
    

class Report(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('removed', 'Removed'),
    )

    REPORT_REASON_CHOICES = (
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate', 'Hate Speech'),
        ('sexual', 'Sexual Content'),
        ('violence', 'Violence'),
        ('copyright', 'Copyright'),
        ('other', 'Other'),
    )

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports'
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports'
    )

    reason = models.CharField(
        max_length=30,
        choices=REPORT_REASON_CHOICES
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.story:
            target = f'Story: {self.story.title}'
        elif self.comment:
            target = f'Comment #{self.comment.id}'
        else:
            target = 'Unknown'

        return f'{target} reported by {self.reporter.username}'