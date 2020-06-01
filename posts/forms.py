from django import forms

from .models import Comment, Post


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий'}
        widgets = {'text': forms.Textarea({'rows': 3})}
