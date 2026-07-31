from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Story


class StoryForm(forms.ModelForm):

    class Meta:
        model = Story

        fields = [
            'title',
            'category',
            'summary',
            'cover_image',
            'content',
            'status',
        ]

        widgets = {
            'content': SummernoteWidget(),
        }