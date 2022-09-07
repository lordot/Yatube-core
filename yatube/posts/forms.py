from django import forms

from .models import Post, Comment


class BaseForm(forms.ModelForm):
    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Необходимо написать что-то')
        return data


class PostForm(BaseForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(BaseForm):
    class Meta:
        model = Comment
        fields = ('text',)
