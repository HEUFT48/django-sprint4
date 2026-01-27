from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Введите комментарий'
            })
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image', 'category', 'location', 'pub_date']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'password': forms.HiddenInput(),
        }


class SimpleCommentForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 3, 'placeholder': 'Введите комментарий'})
    )
