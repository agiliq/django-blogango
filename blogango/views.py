from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.encoding import smart_str
from django.db.models import Q
from django.views.decorators.http import require_POST
import json
from django.views.generic.dates import MonthArchiveView
from django.views import generic
from taggit.models import Tag

from blogango.models import Blog, BlogEntry, Comment, BlogRoll, Reaction
from blogango import forms as bforms
from blogango.conf.settings import AKISMET_COMMENT, AKISMET_API_KEY
from blogango.akismet import Akismet, AkismetError


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class StaffMemReqMixin(object):

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffMemReqMixin, self).dispatch(*args, **kwargs)


class AdminDashboardView(StaffMemReqMixin, generic.ListView):
    template_name = 'blogango/admin/index.html'
    context_object_name = 'recent_drafts'

    def get_queryset(self, *args, **kwargs):
        recent_drafts = BlogEntry.default.filter(is_published=False).order_by('-created_on')[:5]
        return recent_drafts

    def get_context_data(self, *args, **kwargs):
        context = super(AdminDashboardView, self).get_context_data(**self.kwargs)
        recent_entries = BlogEntry.objects.order_by('-created_on')[:5]
        context['recent_entries'] = recent_entries
        return context

admin_dashboard = AdminDashboardView.as_view()


@staff_member_required
def admin_entry_edit(request, entry_id=None):
    entry = None
    entry_form = bforms.EntryForm(initial={'created_by': request.user.id,
                                           'publish_date': datetime.now()})
    if entry_id:
        entry = get_object_or_404(BlogEntry, pk=entry_id)
        entry_form = bforms.EntryForm(instance=entry,
                                      initial={'text': entry.text.raw})
    if request.POST:
        entry_form = bforms.EntryForm(request.POST, instance=entry)

        if entry_form.is_valid():
            new_entry = entry_form.save(commit=False)
            if "publish" in request.POST:
                new_entry.is_published = True
            if "page" in request.POST:
                new_entry.is_page = True
            new_entry.save()
            tag_list = entry_form.cleaned_data['tags']
            new_entry.tags.set(*tag_list)
            if new_entry.is_published:
                return redirect(new_entry)
            return redirect(reverse('blogango_admin_entry_edit',
                                    args=[new_entry.id])+'?done')
    tags_json = json.dumps([each.name for each in Tag.objects.all()])
    return render('blogango/admin/edit_entry.html', request, {'entry_form':
                                                              entry_form,
                                                              'entry': entry,
                                                              'tags_json':
                                                              tags_json})


@staff_member_required
def admin_manage_entries(request, username=None):
    author = None
    if username:
        author = get_object_or_404(User, username=username)
        entries = BlogEntry.default.filter(created_by=author)
    else:
        entries = BlogEntry.default.all()
    return render('blogango/admin/manage_entries.html',
                  request, {'entries': entries, 'author': author})


@staff_member_required
def admin_manage_comments(request, entry_id=None):
    # fetch all comments, objects gets you only public ones
    blog_entry = None
    if entry_id:
        blog_entry = get_object_or_404(BlogEntry, pk=entry_id)
    if 'blocked' in request.GET:
        comments = \
            Comment.default.filter(Q(is_spam=True) | Q(is_public=False)).order_by('-created_on')
    else:
        comments = Comment.objects.order_by('-created_on')
    if blog_entry:
        comments = comments.filter(comment_for=blog_entry)
    page = request.GET.get('page', 1)
    comments_per_page = getattr(settings, 'COMMENTS_PER_PAGE', 20)
    paginator = Paginator(comments, comments_per_page)
    page_ = paginator.page(page)
    comments = page_.object_list
    return render('blogango/admin/manage_comments.html',
                  request, {'comments': comments,
                            'blog_entry': blog_entry,
                            'page_': page_})


@staff_member_required
def admin_edit_preferences(request):
    #only one blog must be present
    blog = Blog.objects.get_blog()
    form = bforms.PreferencesForm(instance=blog)
    if request.POST:
        form = bforms.PreferencesForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            return redirect(request.path+"?done")
    return render('blogango/admin/edit_preferences.html', request, {'form': form})


@staff_member_required
@require_POST
def admin_comment_approve(request):
    comment_id = request.POST.get('comment_id', None)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_spam = False
    comment.is_public = True
    comment.save()
    return HttpResponse(comment.pk)


@staff_member_required
@require_POST
def admin_comment_block(request):
    comment_id = request.POST.get('comment_id', None)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_public = False
    comment.save()
    return HttpResponse(comment.pk)

class IndexView(generic.ListView):
    template_name = 'blogango/mainpage.html'
    context_object_name = 'entries'

    def get_queryset(self, *args, **kwargs):
        blog = Blog.objects.get_blog()
        if not blog:
            return HttpResponseRedirect(reverse('blogango_install'))
        entries = BlogEntry.objects.filter(is_page=False)
        return entries

    def get_context_data(self, *args, **kwargs):
        blog = Blog.objects.get_blog()
        if blog:
            context = super(IndexView, self).get_context_data(**kwargs)
            queryset = context['entries']
            (paginator, page_, queryset, is_paginated) = self.paginate_queryset(queryset, blog.entries_per_page)
            if paginator.num_pages < 1:
                return redirect(reverse('blogango_page', args=[paginator.num_pages]))
            context['page_'] = page_
            return context

index = IndexView.as_view()



def check_comment_spam(request, comment):
    api = Akismet(AKISMET_API_KEY,
                  'http://%s' % (request.get_host()),
                  request.META.get('HTTP_USER_AGENT', ''))

    message = "Akismet API key is invalid."
    try:
        is_verified = api.verify_key()
    except AkismetError, e:
        is_verified = False
    if is_verified:
        akismet_data = {'user_ip': request.META['REMOTE_ADDR'],
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'comment_author': smart_str(comment.user_name),
                        'comment_author_email': smart_str(comment.email_id),
                        'comment_author_url': smart_str(comment.user_url),
                        'comment_type': 'comment'}

        return api.comment_check(smart_str(comment.text), akismet_data)
    raise AkismetError(message)

class DetailsView(generic.DetailView):
    template_name = 'blogango/details.html'
    model = BlogEntry

    def get_context_data(self, *args, **kwargs):
        context = super(DetailsView, self).get_context_data(**kwargs)
        if not _is_blog_installed():
            template_name = 'blogango/install'
        entry = BlogEntry.default.get(created_on__year=self.kwargs['year'],
                                      created_on__month=self.kwargs['month'],
                                      slug=self.kwargs['slug'])
        # published check needs to be handled here to allow previews
        if not entry.is_published:
            if self.request.user.is_staff and 'preview' in self.request.GET:
                pass
            else:
                raise Http404
        init_data = {}
        if self.request.user.is_authenticated():
            init_data['name'] = self.request.user.get_full_name() or self.request.user.username
            init_data['email'] =self.request.user.email
        else:
            init_data['name'] = self.request.session.get("name", "")
            init_data['email'] = self.request.session.get("email", "")
            init_data['url'] = self.request.session.get("url", "")
        comment_f = bforms.CommentForm(initial=init_data)
        comments = Comment.objects.filter(comment_for=entry, is_spam=False)
        reactions = Reaction.objects.filter(comment_for=entry)
        payload = {'entry': entry, 'comments': comments,
               'reactions': reactions, 'comment_form': comment_f}
        for k,v in payload.items():
            context[k] = v
        return context

    def post(self, *args, **kwargs):
        comment_f = bforms.CommentForm(self.request.POST)
        if comment_f.is_valid():
            entry = self.get_object()
            print "absolute url is ", entry.get_absolute_url()
            comment_by = self.request.user if self.request.user.is_authenticated() else None
            comment = Comment(text=comment_f.cleaned_data['text'],
                              created_by=comment_by,
                              comment_for=entry,
                              user_name=comment_f.cleaned_data['name'],
                              user_url=comment_f.cleaned_data['url'],
                              email_id=comment_f.cleaned_data['email'])
            comment.is_public = getattr(settings, 'AUTO_APPROVE_COMMENTS',
                                        True)
            if AKISMET_COMMENT:
                try:
                    comment.is_spam = check_comment_spam(self.request, comment)
                except AkismetError:
                    # Most likely could be a timeout to a spam message
                    comment.is_spam = True
            if not comment.is_spam:
                print "comment is not spam"
                self.request.session["name"] = comment_f.cleaned_data['name']
                self.request.session["email"] = comment_f.cleaned_data['email']
                self.request.session["url"] = comment_f.cleaned_data['url']
            comment.save()
            return HttpResponseRedirect('#comment-%s' % comment.pk)
details = DetailsView.as_view()

#@handle404
def page_details(request, slug):
    if not _is_blog_installed():
        return HttpResponseRedirect(reverse('blogango_install'))

    entry = BlogEntry.default.get(is_page=True,
                                  slug=slug)

    # published check needs to be handled here to allow previews
    if not entry.is_published:
        if request.user.is_staff and 'preview' in request.GET:
            pass
        else:
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
            comment.is_public = getattr(settings, 'AUTO_APPROVE_COMMENTS',
                                        True)
            if AKISMET_COMMENT:
                try:
                    comment.is_spam = check_comment_spam(request, comment)
                except AkismetError:
                    # Most likely spam causing timeout error.
                    comment.is_spam = True
            comment.save()
            return HttpResponseRedirect('#comment-%s' % comment.pk)
    else:
        init_data = {'name': None}
        if request.user.is_authenticated():
            init_data['name'] = request.user.get_full_name() or request.user.username
        comment_f = bforms.CommentForm(initial=init_data)

    comments = Comment.objects.filter(comment_for=entry, is_spam=False)
    reactions = Reaction.objects.filter(comment_for=entry)
    # tags = Tag.objects.filter(tag_for=entry)
    payload = {'entry': entry, 'comments': comments,
               'reactions': reactions, 'comment_form': comment_f}
    return render('blogango/details.html', request, payload)


class TagDetails(generic.ListView):
    template_name = 'blogango/tag_details.html'
    context_object_name = 'tagged_entries'

    def get_queryset(self, *args, **kwargs):
        tag = get_object_or_404(Tag, slug= self.kwargs['tag_slug'])
        tagged_entries = BlogEntry.objects.filter(is_published=True, tags__in=[tag])
        return tagged_entries

    def get_context_data(self, page=1,*args, **kwargs):
        tag = get_object_or_404(Tag, slug= self.kwargs['tag_slug'])
        context = super(TagDetails, self).get_context_data(**kwargs)
        blog = Blog.objects.get_blog()
        page = int(page)
        tagged_entries = context['tagged_entries']
        paginator = Paginator(tagged_entries, blog.entries_per_page)
        if page > paginator.page(page):
            return redirect(reverse(self.template_name, args=[tag.slug, paginator.num_pages]))
        page_ = paginator.page(page)
        entries = page_.object_list
        context['tag'] = tag
        context['entries'] = entries
        context['page_'] = page_
        return context

tag_details = TagDetails.as_view()

class InstallBlog(LoginRequiredMixin, generic.View):
    form_class = bforms.InstallForm
    template_name = 'blogango/index.html'
    context_object_name = 'install_form'

    def get(self, request, *args, **kwargs):
        if _is_blog_installed():
            return HttpResponseRedirect(reverse('blogango_index'))
        install_form = self.form_class
        return install_form

    def post(self, request, *args, **kwargs):
        if _is_blog_installed():
            template_name = 'blogango/install.html'
        install_form = self.form_class(request.POST)
        if install_form.is_valid():
            install_form.save()
        return install_form
install_blog = InstallBlog.as_view()

class CreateBlogRoll(LoginRequiredMixin, generic.edit.FormView):
    template_name = 'blogango/blogroll.html'
    form_class = bforms.BlogForm
    context_object_name = 'blogroll_form'

    def get_context_data(self, *args, **kwargs):
        context = super(CreateBlogRoll, self).get_context_data(**kwargs)
        context['blogroll_form'] = self.form_class()
        return context

    def post(self, *args, **kwargs):
        blogroll_form = self.form_class(self.request.POST)
        if blogroll_form.is_valid():
            blogroll_form.save()
            return HttpResponseRedirect('.')
        payload = {"blogroll_form": blogroll_form}  
        return render(self.template_name, self.request, payload)

create_blogroll = CreateBlogRoll.as_view()

class AuthorView(generic.ListView):
    template_name = 'blogango/author.html'

    def get_queryset(self, *args, **kwargs):
        author = get_object_or_404(User, username = self.kwargs['username'])
        author_posts = author.blogentry_set.filter(is_published=True)
        return author_posts

    def get_context_data(self, page=1, *args, **kwargs):
        context = super(AuthorView, self).get_context_data(**self.kwargs)
        author_posts = context['object_list']
        page = int(page)
        blog = Blog.objects.get_blog()
        paginator = Paginator(author_posts, blog.entries_per_page)
        author = get_object_or_404(User, username = self.kwargs['username'])
        if page > paginator.num_pages:
            return redirect(reverse(self.template_name, args=[author, paginator.num_pages]))
        page_ = paginator.page(page)
        entries = page_.object_list
        context['entries'] = entries
        context['author'] = author
        context['page_'] = page_
        return context


author = AuthorView.as_view()


class BlogEntryMonthArchiveView(MonthArchiveView):
    queryset = BlogEntry.objects.filter(is_page=False, is_published=True)
    date_field = 'created_on'
    template_name = 'blogango/archive_view.html'
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super(BlogEntryMonthArchiveView, self).get_context_data(**kwargs)
        context.update(_get_sidebar_objects(self.request))
        return context

monthly_view = BlogEntryMonthArchiveView.as_view()


#Helper methods.
def _is_blog_installed():
    return Blog.objects.get_blog()


def render(template, request, payload):
    """Wrapper on render_to_response.
    Adds sidebar objects. Adds RequestContext"""
    payload.update(_get_sidebar_objects(request))
    return render_to_response(template, payload,
                              context_instance=RequestContext(request),)


def _get_sidebar_objects(request):
    """Gets the objects which are always displayed in the sidebar"""
    blog = Blog.objects.get_blog()
    if not blog:
        return {}
    recents = \
        BlogEntry.objects.filter(is_page=False,
                                 is_published=True).order_by('-created_on')[:blog.recents]
    blogroll = BlogRoll.objects.filter(is_published=True)
    return {'blog': blog,
            'recents': recents,
            'blogroll': blogroll,
            'canonical_url': request.build_absolute_uri(),
            'pingback_xmlrpc_url':
            request.build_absolute_uri(reverse('xmlrpc')), }


def _get_archive_months():
    """Get the months for which at least one entry exists"""
    dates = BlogEntry.objects.filter(is_page=False,
                                     is_published=True).dates('created_on',
                                                              'month',
                                                              order='DESC')
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


# A generic form processor.
def generic(request):
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        pass


