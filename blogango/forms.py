
from django import forms

from blogango.models import Blog, BlogRoll

class WideTextArea(forms.Textarea):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('attrs',{}).update({'rows': '20', 'cols':'80'})
        super(WideTextArea, self).__init__(*args, **kwargs)

class EntryForm(forms.Form):
    title = forms.CharField(max_length=100, required=False) 
    text = forms.CharField(widget=WideTextArea, label='Entry')
    slug = forms.CharField(max_length=100, required=False) 
    tags = forms.CharField(max_length=100, required=False)
    is_page = forms.BooleanField(initial=False, label='Is it a page?', required=False)
    comments_allowed = forms.BooleanField(initial=True, label='Are comments allowed?', required=False)
    is_rte = forms.BooleanField(initial=True, label='Use Rick Text?', required=False)

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea'}), label='Comment')
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'textfield'}))
    url = forms.URLField(required=False, widget=forms.TextInput(attrs={'class': 'textfield'})) 
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'textfield'}))

class TagForm(forms.Form):
    tag_txt = forms.CharField(max_length=100, label='Tag as') 

class InstallForm(forms.ModelForm):
    
    class Meta:
        model = Blog
        exclude = ('entries_per_page', 'recents', 'recent_comments')

class PreferencesForm(forms.ModelForm):
    
    class Meta:
        model = Blog
        exclude = ('title', 'tag_line')
        
class BlogForm(forms.ModelForm):
    
    class Meta:
        model = BlogRoll
        exclude = ('is_published',)   
        