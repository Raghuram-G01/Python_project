"""Forms for the blog app."""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML, Div
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from taggit.forms import TagWidget

from .models import BlogPost, Category


class BlogPostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'content', 'excerpt', 'featured_image', 'featured_image_alt',
            'category', 'tags', 'status', 'meta_description', 'meta_keywords',
            'is_featured', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter an engaging title...',
                'class': 'form-control'
            }),
            'content': CKEditorUploadingWidget(),
            'excerpt': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Brief description of your post (optional - will be auto-generated)...',
                'class': 'form-control'
            }),
            'featured_image_alt': forms.TextInput(attrs={
                'placeholder': 'Alt text for featured image...',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={
                'placeholder': 'Add tags separated by commas...',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Meta description for SEO (optional - will be auto-generated)...',
                'class': 'form-control',
                'maxlength': 160
            }),
            'meta_keywords': forms.TextInput(attrs={
                'placeholder': 'SEO keywords separated by commas...',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Basic Information
            HTML('<h4 class="mb-3">Basic Information</h4>'),
            'title',
            'content',
            'excerpt',
            
            # Media
            HTML('<h4 class="mb-3 mt-4">Featured Image</h4>'),
            Row(
                Column('featured_image', css_class='form-group col-md-8 mb-0'),
                Column('featured_image_alt', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            
            # Categorization
            HTML('<h4 class="mb-3 mt-4">Categorization</h4>'),
            Row(
                Column('category', css_class='form-group col-md-6 mb-0'),
                Column('tags', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            
            # Publishing Options
            HTML('<h4 class="mb-3 mt-4">Publishing Options</h4>'),
            Row(
                Column('status', css_class='form-group col-md-4 mb-0'),
                Column(
                    Field('is_featured', css_class='form-check-input'),
                    css_class='form-group col-md-4 mb-0'
                ),
                Column(
                    Field('allow_comments', css_class='form-check-input'),
                    css_class='form-group col-md-4 mb-0'
                ),
                css_class='form-row'
            ),
            
            # SEO Settings
            HTML('<h4 class="mb-3 mt-4">SEO Settings</h4>'),
            'meta_description',
            'meta_keywords',
            
            # Submit Buttons
            HTML('<hr class="my-4">'),
            Div(
                Submit('save_draft', 'Save as Draft', css_class='btn btn-secondary mr-2'),
                Submit('publish', 'Publish Post', css_class='btn btn-primary'),
                css_class='text-right'
            )
        )
        
        # Make some fields optional
        self.fields['excerpt'].required = False
        self.fields['featured_image'].required = False
        self.fields['featured_image_alt'].required = False
        self.fields['category'].required = False
        self.fields['meta_description'].required = False
        self.fields['meta_keywords'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set status based on which button was clicked
        if 'publish' in self.data:
            instance.status = 'published'
        elif 'save_draft' in self.data:
            instance.status = 'draft'
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships (tags)
        
        return instance


class SearchForm(forms.Form):
    """Search form for blog posts."""
    
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search posts...',
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    tag = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by tag...',
            'class': 'form-control'
        }),
        required=False
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('-published_at', 'Newest First'),
            ('published_at', 'Oldest First'),
            ('-view_count', 'Most Popular'),
            ('-like_count', 'Most Liked'),
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='-published_at',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-4 mb-0'),
                Column('category', css_class='form-group col-md-3 mb-0'),
                Column('tag', css_class='form-group col-md-3 mb-0'),
                Column('sort_by', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Submit('search', 'Search', css_class='btn btn-primary')
        )
