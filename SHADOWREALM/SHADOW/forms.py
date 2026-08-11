from django import forms
from django_summernote.widgets import SummernoteWidget
from django.forms import inlineformset_factory

from .models import Story, StoryScene


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
            'horror_mode',
        ]

        widgets = {
            'content': SummernoteWidget(),

            'horror_mode': forms.CheckboxInput(
                attrs={
                    'class': 'horror-toggle'
                }
            ),
        }


class StorySceneForm(forms.ModelForm):

    class Meta:
        model = StoryScene

        fields = [
            'text',
            'image',
            'audio',
            'is_jumpscare',
            'jumpscare_image',
            'jumpscare_audio',
        ]

        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Write what happens in this scene...'
            }),

            'is_jumpscare': forms.CheckboxInput(
                attrs={
                    'class': 'jumpscare-toggle'
                }
            ),
        }


StorySceneFormSet = inlineformset_factory(
    Story,
    StoryScene,
    form=StorySceneForm,
    extra=1,
    can_delete=True
)