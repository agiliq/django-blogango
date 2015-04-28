from django.contrib.auth.models import User
from django import forms
from django.contrib.admin import widgets

from blogango.models import Blog, BlogRoll, BlogEntry


class WideTextArea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs', {}).update({'rows': '20', 'cols': '80'})
        super(WideTextArea, self).__init__(*args, **kwargs)


class EntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.filter(is_staff=True)
        self.fields['publish_date'].widget = widgets.AdminSplitDateTime()

    title = forms.CharField(max_length=100,
                            required=False,
                            widget=forms.TextInput(attrs={'size': '40'}))
    text = forms.CharField(widget=WideTextArea(attrs={'class': 'resizable'}))

    class Meta:
        model = BlogEntry
        exclude = ('slug', 'summary')


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea'}),
                           label='Comment')
    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs={'class':
                                                         'textfield'}))
    url = forms.URLField(required=False,
                         widget=forms.TextInput(attrs={'class': 'textfield'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':
                                                           'textfield'}))


class InstallForm(forms.ModelForm):

    class Meta:
        model = Blog
        exclude = ('entries_per_page', 'recents', 'recent_comments')


class PreferencesForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ('title', 'tag_line', 'entries_per_page', 'recents', 'recent_comments')


class BlogForm(forms.ModelForm):
    class Meta:
        model = BlogRoll
        exclude = ('is_published',)
