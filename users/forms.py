"""Forms for the users app."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML

from .models import UserProfile, Newsletter, ContactMessage


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            'password1',
            'password2',
            Submit('submit', 'Create Account',
                   css_class='btn btn-primary btn-block')
        )

        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['password1', 'password2']:
                field.widget.attrs['autocomplete'] = 'new-password'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserAccountForm(forms.ModelForm):
    """User account information form."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
        )

        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.required = True if field_name == 'email' else False


class UserProfileForm(forms.ModelForm):
    """User profile form."""

    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'website', 'location', 'birth_date',
            'twitter_username', 'github_username', 'linkedin_username',
            'show_email'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'maxlength': '500'
            }),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'twitter_username': forms.TextInput(attrs={'placeholder': 'username (without @)'}),
            'github_username': forms.TextInput(attrs={'placeholder': 'username'}),
            'linkedin_username': forms.TextInput(attrs={'placeholder': 'username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'bio',
            'avatar',
            Row(
                Column('website', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'birth_date',
            HTML(
                '<h5 class="mt-4 mb-3 text-gray-700 font-semibold">Social Media Links</h5>'),
            Row(
                Column('twitter_username', css_class='form-group col-md-4 mb-0'),
                Column('github_username', css_class='form-group col-md-4 mb-0'),
                Column('linkedin_username',
                       css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            HTML('<h5 class="mt-4 mb-3 text-gray-700 font-semibold">Privacy Settings</h5>'),
            'show_email',
        )

        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            if field_name != 'show_email':
                field.widget.attrs['class'] = 'form-control'

    def clean_twitter_username(self):
        username = self.cleaned_data.get('twitter_username')
        if username and username.startswith('@'):
            username = username[1:]  # Remove @ if user added it
        return username

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        return website

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (5MB limit)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    'Image file too large. Please keep it under 5MB.')

            # Check file type
            if not avatar.content_type.startswith('image/'):
                raise forms.ValidationError(
                    'Please upload a valid image file.')

            # Check image dimensions (optional - for very large images)
            try:
                from PIL import Image
                img = Image.open(avatar)
                if img.width > 4000 or img.height > 4000:
                    raise forms.ValidationError(
                        'Image dimensions too large. Please use an image smaller than 4000x4000 pixels.')
            except Exception:
                # If PIL is not available or image can't be processed, allow it
                pass

        return avatar


class PasswordChangeForm(forms.Form):
    """Custom password change form."""

    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current Password'
        }),
        label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        label='New Password',
        help_text='Password must be at least 8 characters long.'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        }),
        label='Confirm New Password'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'current_password',
            'new_password1',
            'new_password2',
        )

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('New passwords do not match.')
        return password2

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password and len(password) < 8:
            raise forms.ValidationError(
                'Password must be at least 8 characters long.')
        return password

    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form."""

    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Your name (optional)',
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False


class ContactForm(forms.ModelForm):
    """Contact form."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your full name',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'your.email@example.com',
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'What is this about?',
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Your message...',
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'subject',
            'message',
            Submit('submit', 'Send Message', css_class='btn btn-primary')
        )
