from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.views.generic.date_based import archive_month
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from blogango.models import Blog, BlogEntry, Comment, BlogRoll
from blogango import forms as bforms

from blogango.conf.settings import AKISMET_COMMENT, AKISMET_API_KEY

def welcome(request):
    return render_to_response('mainpage.html', {})


def handle404(view_function):
    def wrapper(*args, **kwargs):
        try:
            return view_function(*args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404
    return wrapper


def index(request, page = 1):
    if not _is_blog_installed():
        return HttpResponseRedirect(reverse('blogango_install'))
    page = int(page)
    blog = Blog.objects.all()[0]
    entries = BlogEntry.objects.filter(is_page=False, is_published=True).order_by('-created_on')
    paginator = Paginator(entries, blog.entries_per_page)
    page_ = paginator.page(page)
    entries = page_.object_list
    has_next = page_.has_next()
    has_prev = page_.has_previous()
    next = page + 1
    prev = page - 1
    payload = locals()
    return render('blogango/mainpage.html', request, payload)


def check_comment_spam(request, comment):
    from blogango.akismet import Akismet, APIKeyError
    api = Akismet(AKISMET_API_KEY, request.get_host(), request.META['HTTP_USER_AGENT'])
    
    if api.verify_key():
        akismet_data = {'user_ip': request.META['REMOTE_ADDR'], 
                        'user_agent': request.META['HTTP_USER_AGENT'], 
                        'comment_author': comment.user_name, 
                        'comment_author_email': comment.email_id, 
                        'comment_author_url': comment.user_url, 
                        'comment_type': 'comment'}

        return api.comment_check(comment.text, akismet_data)
    raise APIKeyError("Akismet API key is invalid.")


@handle404
def details(request, year, month, slug):
    if not _is_blog_installed():
        return HttpResponseRedirect(reverse('blogango_install'))
    
    entry = BlogEntry.objects.get(created_on__year=year, 
                                  created_on__month=month, 
                                  slug=slug,
                                  is_published=True)

    if not entry.is_published:
        raise Http404

    if request.method == 'POST':
        comment_f = bforms.CommentForm(request.POST)
        if comment_f.is_valid():
            comment_by = request.user if request.user.is_authenticated() else None
            comment = Comment(text=comment_f.cleaned_data['text'], 
                              created_by=comment_by, 
                              comment_for=entry, 
                              user_name=comment_f.cleaned_data['name'],
                              user_url=comment_f.cleaned_data['url'], 
                              email_id=comment_f.cleaned_data['email'])
            if AKISMET_COMMENT:
                comment.is_spam = check_comment_spam(request, comment)
            comment.save()
            return HttpResponseRedirect('.')
    else:
        comment_f = bforms.CommentForm()
            
    comments = Comment.objects.filter(comment_for=entry, is_spam=False)
    # tags = Tag.objects.filter(tag_for=entry)
    payload = {'entry': entry, 'comments': comments, 'comment_form': comment_f}
    return render('blogango/details.html', request, payload)
 

@handle404
def comment_details(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    payload = locals()
    return render('blogango/comment.html', request, payload)         
       

def tag_details(request, tag_slug):
    from taggit.models import Tag
    if Tag.objects.filter(slug=tag_slug).count() == 0:
        raise Http404
    tag = Tag.objects.get(slug=tag_slug)
    entries = BlogEntry.objects.filter(is_published=True, tags__in=[tag])
    feed_url = getattr(settings, 'FEED_URL', reverse('blogango_feed', args=['tag']) + tag.slug + '/')
    payload = {'tag': tag, 'entries': entries, 'feed_url': feed_url}
    return render('blogango/tag_details.html', request, payload)    


@login_required
def create_entry(request):
    if request.method == 'GET':
        create = bforms.EntryForm()
    elif request.method == 'POST':
        create = bforms.EntryForm(request.POST)
        if create.is_valid():
            if request.POST.has_key('save'):
                publish = False
            elif request.POST.has_key('post'):
                publish = True       
            entry = BlogEntry(created_by=request.user, 
                              text=create.cleaned_data['text'], 
                              title=create.cleaned_data['title'], 
                              slug=create.cleaned_data['slug'], 
                              is_page=create.cleaned_data['is_page'], 
                              is_published=publish, 
                              is_rte=create.cleaned_data['is_rte'])
            entry.save()
            tags = create.cleaned_data['tags']
            tag_list = tags.split()
            for tag in tag_list:
                tag_, created = Tag.objects.get_or_create(tag_txt=tag.strip())
                tag_.save()
                entry.tag_set.add(tag_)
            if request.POST.has_key('save'):
                return HttpResponseRedirect('.')
            elif request.POST.has_key('post'):
                return HttpResponseRedirect(entry.get_absolute_url())
    payload = {'create_form': create,}
    return render('blogango/create.html', request, payload)


@login_required
def edit_entry(request, entry_id):
    if request.method == 'GET':
        entry = BlogEntry.objects.filter(id=entry_id).values()[0]
        entry_ = BlogEntry.objects.get(id=entry_id)
        tags = Tag.objects.filter(tag_for=entry_)
        tags = [tag.tag_txt for tag in tags]
        tag_ = " ".join(tags)
        entry['tags'] = tag_
        create = bforms.EntryForm(entry)
    elif request.method == 'POST':
        create = bforms.EntryForm(request.POST)
        if create.is_valid():
            entry = BlogEntry.objects.get(id=entry_id)
            entry.text = create.cleaned_data['text']
            entry.title = create.cleaned_data['title']
            entry.slug = create.cleaned_data['slug']
            entry.is_page = create.cleaned_data['is_page']
            entry.comments_allowed = create.cleaned_data['comments_allowed']
            if request.POST.has_key('save'):
               publish = False
            elif request.POST.has_key('post'):
               publish = True   
            entry.is_published = publish
            entry.save()
            tags = Tag.objects.filter(tag_for=entry)
            for tag in tags:
               entry.tag_set.remove(tag)
            tags_data = create.cleaned_data['tags']
            tag_list = tags_data.split(' ')
            for tag in tag_list:
                tag_, created = Tag.objects.get_or_create(tag_txt=tag.strip())
                tag_.save()
                entry.tag_set.add(tag_)
            return HttpResponseRedirect(entry.get_absolute_url())
    payload = {'create_form': create,}
    return render('blogango/create.html', request, payload)


@login_required
def mod_entries(request):
    if request.method == 'GET':
        entries = BlogEntry.objects.all()
        payload = locals()
        return render('blogango/manage_entries.html', request, payload)
    if request.method == 'POST':
        if request.POST.has_key("unpublish"):
            entry_ids = request.POST['entries']
            entries = BlogEntry.objects.filter(id__in=entry_ids)
            for entry in entries:
                entry.is_published = False
                entry.save()
        elif request.POST.has_key("del"):
            entry_ids = request.POST['entries']
            # print request.POST
            # print entry_ids
            BlogEntry.objects.filter(id__in=entry_ids).delete()                
        return HttpResponseRedirect('.')


@login_required 
def moderate_comments(request):
    if request.method == 'GET':
        comments = Comment.objects.filter()
        payload = {"comments": comments}
        return render('blogango/mod_comment.html', request, payload)
    elif request.method == 'POST':
        if request.POST.has_key('spam'):
            spammeds = request.POST['spam']
        else:
            spammeds = {}
        for spammed in spammeds:
             comment = Comment.objects.get(id = spammed)
             comment.is_spam = True
             comment.save()
        if request.POST.has_key('delete'):
            deleteds = request.POST['delete']
        else:
            deleteds = {}
        for deleted in deleteds:
            Comment.objects.get(id = deleted).delete()
        return HttpResponseRedirect('.')


@login_required
def install_blog(request):
    if _is_blog_installed():
        return HttpResponseRedirect(reverse('blogango_index'))
    
    if request.method == 'GET':
        install_form = bforms.InstallForm()
    if request.method == 'POST':
       install_form = bforms.InstallForm(request.POST)
       if install_form.is_valid():
          install_form.save()         
          return HttpResponseRedirect(reverse('blogango_index'))
    payload = {"install_form": install_form}
    return render('blogango/install.html', request, payload)


@login_required
def  create_blogroll(request):
    if request.method == 'GET':
        blogroll_form = bforms.BlogForm()
    if request.method == 'POST':
        blogroll_form = bforms.BlogForm(request.POST)
        if blogroll_form.is_valid():
            blogroll_form.save()
            return HttpResponseRedirect('.')
    payload = {"blogroll_form": blogroll_form}
    return render('blogango/blogroll.html', request, payload)    


@login_required
def edit_preferences(request):
    if request.method == 'GET':
        prefs_form = bforms.PreferencesForm(Blog.objects.all().values()[0])
    if request.method == 'POST':
        prefs_form = bforms.PreferencesForm(request.POST)
        if prefs_form.is_valid():
            blog = Blog.objects.all()[0]
            # print blog.id
            blog.entries_per_page = prefs_form.cleaned_data['entries_per_page']
            blog.recents = prefs_form.cleaned_data['recents']     
            blog.recent_comments = prefs_form.cleaned_data['recents']
            blog.save()
            return HttpResponseRedirect('.')
    payload = {"install_form": prefs_form}
    return render('blogango/edit_preferences.html', request, payload)  


@login_required
def manage(request):
    return render('blogango/manage.html', request, {})   


def author(request, username):
    author = get_object_or_404(User, username=username)
    return render('blogango/author.html', request, {'author': author})
    
    
def monthly_view(request, year, month):
    # print year, month
    queryset = BlogEntry.objects.filter(is_page=False, is_published=True)
    return archive_month(request=request, 
                         template_name='blogango/archive_view.html', 
                         year=year, 
                         month=month, 
                         queryset=queryset, 
                         date_field='created_on', 
                         extra_context=_get_sidebar_objects(request))
             

#Helper methods.
def _is_blog_installed():
    if Blog.objects.count() == 0:
        return False
    return True
       
        
def render (template, request, payload):
    """Wrapper on render_to_response.
    Adds sidebar objects. Adds RequestContext"""
    payload.update(_get_sidebar_objects(request))
    return render_to_response(template, payload, context_instance=RequestContext(request),)


def _get_sidebar_objects (request):
    """Gets the objects which are always displayed in the sidebar"""
    try:
       blog = Blog.objects.all()[0]
    except:
       return {}
    recents = BlogEntry.objects.filter(is_page = False, is_published = True).order_by('-created_on')[:blog.recents]
    blogroll = BlogRoll.objects.all()
    pages = BlogEntry.objects.filter(is_page = True, is_published = True)
    recent_comments = Comment.objects.all().order_by('-created_on')[:blog.recent_comments]
    # date_list = _get_archive_months()
    return {'blog':blog, 'recents':recents, 'pages':pages, 'blogroll':blogroll, 'recent_comments':recent_comments}


def _get_archive_months():
    """Get the months for which at least one entry exists"""
    dates = BlogEntry.objects.dates('created_on', 'month', order='DESC')
    # print dates
    # date_list = []
    # for date in dates:
    #     date_list.append((date.strftime('%Y/%b'), date.strftime('%B %y')))
    return dates


def _generic_form_display(request, form_class):
    if request.method == 'GET':
        form_inst = form_class()
    if request.method == 'POST':
        form_inst = form_class(request.POST)
        if form_inst.is_valid():
            form_inst.save()         
            return HttpResponseRedirect('.')
    payload = {"install_form": form_inst}
    return render('blogango/install.html', request, payload)
        

def generic(request): # A generic form processor.
    if request.method == 'GET':
        pass
    if request.method == 'POST':
       pass
        
