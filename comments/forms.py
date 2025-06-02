"""Forms for the comments app."""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, HTML

from .models import Comment, CommentFlag


class CommentForm(forms.ModelForm):
    """Form for adding/editing comments."""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts...',
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('content', css_class='mb-3'),
            Submit('submit', 'Post Comment', css_class='btn btn-primary')
        )


class CommentReplyForm(CommentForm):
    """Form for replying to comments."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Write a reply...',
            'rows': 3
        })
        self.helper.layout = Layout(
            Field('content', css_class='mb-3'),
            Submit('submit', 'Post Reply', css_class='btn btn-sm btn-primary')
        )


class CommentFlagForm(forms.ModelForm):
    """Form for flagging inappropriate comments."""
    
    class Meta:
        model = CommentFlag
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Please provide additional details (optional)...',
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('reason', css_class='mb-3'),
            Field('description', css_class='mb-3'),
            HTML('<p class="text-muted small">Flagged comments will be reviewed by our moderation team.</p>'),
            Submit('submit', 'Flag Comment', css_class='btn btn-warning')
        )
