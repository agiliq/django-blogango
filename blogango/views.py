from datetime import datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
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


def handle404(view_function):
    def wrapper(*args, **kwargs):
        try:
            return view_function(*args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404
    return wrapper


class Handle404Mixin(object):
    
    @method_decorator(handle404)
    def dispatch(self, request, *args, **kwargs):
        return super(Handle404Mixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class StaffMemReqMixin(object):

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffMemReqMixin, self).dispatch(*args, **kwargs)


class AdminDashboardView(StaffMemReqMixin, generic.TemplateView):
    template_name = 'blogango/admin/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super(AdminDashboardView, self).get_context_data(**kwargs)
        recent_drafts = BlogEntry.default.filter(is_published=False).order_by('-created_on')[:5]
        recent_entries = BlogEntry.objects.order_by('-created_on')[:5]
        context['recent_entries'] = recent_entries
        context['recent_drafts'] = recent_drafts
        return context

admin_dashboard = AdminDashboardView.as_view()

class AdminCreateUpdateCommon(object):
    model = BlogEntry
    form_class = bforms.EntryForm
    template_name = 'blogango/admin/edit_entry.html'

    def form_valid(self, form):
        if "page" in self.request.POST:
            form.instance.is_page = True
        if "publish" in self.request.POST:
            form.instance.is_published = True
        return super(AdminCreateUpdateCommon, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(AdminCreateUpdateCommon, self).get_context_data(**kwargs)
        tags_json = json.dumps([each.name for each in Tag.objects.all()])
        context['tags_json'] = tags_json
        return context

    def get_success_url(self):
        blog_entry = self.object
        if blog_entry.is_published:
            published_date = blog_entry.publish_date
            return reverse('blogango_details',
                           kwargs={'year': published_date.year,
                                   'month': published_date.month,
                                   'slug': blog_entry.slug})
        else:
            return reverse('blogango_admin_entry_edit',
                           args=[blog_entry.id])+'?done'

class AdminEntryView(StaffMemReqMixin, AdminCreateUpdateCommon, generic.edit.CreateView):

    def get_initial(self):
        initial = super(AdminEntryView, self).get_initial()
        initials = {'created_by': self.request.user.id,
                    'publish_date': datetime.now()}
        initial.update(initials)
        return initial

admin_entry = AdminEntryView.as_view()


class AdminEditView(StaffMemReqMixin, AdminCreateUpdateCommon, generic.UpdateView):
    pass

admin_edit = AdminEditView.as_view()


class AdminManageEntries(StaffMemReqMixin, generic.ListView):
    template_name = 'blogango/admin/manage_entries.html'
    model = BlogEntry
    context_object_name = 'entries'

    def get_queryset(self):
        if self.kwargs:
            username = self.kwargs['username']
            author = get_object_or_404(User, username=username)
            entries = BlogEntry.default.filter(created_by=author)
        else:
            entries = BlogEntry.default.all()
        return entries

    def get_context_data(self, *args, **kwargs):
        context = super(AdminManageEntries, self).get_context_data(**kwargs)
        if self.kwargs:
            username = self.kwargs['username']
            user = get_object_or_404(User, username=username)
            context['author'] = user
        return context 

admin_manage_entries = AdminManageEntries.as_view()


class AdminManageComments(StaffMemReqMixin, generic.ListView):
    model = Comment
    template_name = 'blogango/admin/manage_comments.html'
    context_object_name = 'comments'

    def get_queryset(self):
        blog_entry = None
        if 'entry_id' in self.kwargs:
            blog_entry = get_object_or_404(BlogEntry, pk=self.kwargs['entry_id'])
        if 'blocked' in self.request.GET:
            comments = \
              Comment.default.filter(Q(is_spam=True) | Q(is_public=False)).order_by('-created_on')  
        else:
            comments = Comment.objects.order_by('-created_on')
        if blog_entry:
            comments = comments.filter(comment_for=blog_entry)
        return comments

    def get_context_data(self, *args, **kwargs):
        context = super(AdminManageComments, self).get_context_data(**kwargs)
        blog_entry = None
        if 'entry_id' in self.kwargs:
            blog_entry = get_object_or_404(BlogEntry, pk=self.kwargs['entry_id'])
        context['blog_entry'] = blog_entry
        return context

    def get_paginate_by(self, queryset):
        paginate_by = getattr(settings, 'COMMENTS_PER_PAGE', 20)
        return paginate_by

admin_manage_comments = AdminManageComments.as_view()

class AdminEditPreferences(StaffMemReqMixin, generic.UpdateView):
    model = Blog
    form_class = bforms.PreferencesForm
    template_name = 'blogango/admin/edit_preferences.html'
    success_url = '?done'

    def get_object(self, *args, **kwargs):
        return Blog.objects.get_blog()

admin_edit_preferences = AdminEditPreferences.as_view()



def get_verified_akismet_instance(request):
    api = Akismet(AKISMET_API_KEY,
                  'http://%s' % (request.get_host()),
                  request.META.get('HTTP_USER_AGENT', ''))
    try:
        api.verify_key()
    except AkismetError:
        return False
    return api


def create_akismet_data(comment):
    akismet_data = {'user_ip': smart_str(comment.user_ip),
                    'user_agent': smart_str(comment.user_agent),
                    'comment_author': smart_str(comment.user_name),
                    'comment_author_email': smart_str(comment.email_id),
                    'comment_author_url': smart_str(comment.user_url),
                    'comment_type': 'comment'}
    return akismet_data


@staff_member_required
@require_POST
def admin_comment_approve(request):
    comment_id = request.POST.get('comment_id', None)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_spam = False
    comment.is_public = True
    comment.save()
    api = get_verified_akismet_instance(request)
    if api:
        akismet_data = create_akismet_data(comment)
        api.submit_ham(smart_str(comment.text), akismet_data)
    return HttpResponse(comment.pk)


@staff_member_required
@require_POST
def admin_comment_block(request):
    comment_id = request.POST.get('comment_id', None)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.is_public = False
    comment.save()
    api = get_verified_akismet_instance(request)
    if api:
        akismet_data = create_akismet_data(comment)
        api.submit_spam(smart_str(comment.text), akismet_data)
    return HttpResponse(comment.pk)

class IndexView(generic.ListView):
    template_name = 'blogango/mainpage.html'
    context_object_name = 'entries'
    
    def get_paginate_by(self, queryset):
        paginate_by = self.kwargs['blog'].entries_per_page
        return paginate_by

    def get(self, request, *args, **kwargs):
        blog = Blog.objects.get_blog()
        if not blog:
            return HttpResponseRedirect(reverse('blogango_install'))
        self.kwargs['blog'] = blog
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        entries = BlogEntry.objects.filter(is_page=False)
        return entries

index = IndexView.as_view()

def check_comment_spam(request, comment):
    import logging
    logging.basicConfig(level=logging.INFO)
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
        logging.info(akismet_data)
        logging.info(comment.text)

        is_spam = api.comment_check(smart_str(comment.text), akismet_data)
        logging.info(is_spam)
        return is_spam
    raise AkismetError(message)

class DetailsView(Handle404Mixin, generic.DetailView):
    template_name = 'blogango/details.html'
    context_object_name = 'entry'

    def get(self, request, *args, **kwargs):
        if not _is_blog_installed():
            return HttpResponseRedirect(reverse('blogango_install'))
        return super(DetailsView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if 'year' in self.kwargs:
            entry = BlogEntry.default.get(created_on__year=self.kwargs['year'],
                                      created_on__month=self.kwargs['month'],
                                      slug=self.kwargs['slug'])
        else:
            entry = BlogEntry.default.get(is_page=True, slug=self.kwargs['slug'])

        if not entry.is_published:
            if self.request.user.is_staff and 'preview' in self.request.GET:
                pass
            else:
                raise Http404
        return entry

    def get_context_data(self, **kwargs):
        context = super(DetailsView, self).get_context_data(**kwargs)

        init_data = {}
        if self.request.user.is_authenticated():
            init_data['name'] = self.request.user.get_full_name() or self.request.user.username
            init_data['email'] = self.request.user.email
        else:
            init_data['name'] = self.request.session.get("name", "")
            init_data['email'] = self.request.session.get("email", "")
            init_data['url'] = self.request.session.get("url", "")
        entry = context['entry']
        comment_f = bforms.CommentForm(initial=init_data)
        comments = Comment.objects.filter(comment_for=entry, is_spam=False)
        reactions = Reaction.objects.filter(comment_for=entry)
        payload = {'comments': comments,
               'reactions': reactions, 'comment_form': comment_f}
        context.update(payload)
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        request = self.request
        context = self.get_context_data(object=self.object)
        comment_f = bforms.CommentForm(self.request.POST)
        if comment_f.is_valid():
            comment_by = self.request.user if self.request.user.is_authenticated() else None
            comment = Comment(text=comment_f.cleaned_data['text'],
                              created_by=comment_by,
                              comment_for=self.object,
                              user_name=comment_f.cleaned_data['name'],
                              user_url=comment_f.cleaned_data['url'],
                              email_id=comment_f.cleaned_data['email'])
            comment.is_public = getattr(settings, 'AUTO_APPROVE_COMMENTS',
                                        True)
            comment.user_ip = request.META['REMOTE_ADDR']
            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
            if AKISMET_COMMENT:
                try:
                    comment.is_spam = check_comment_spam(self.request, comment)
                except AkismetError:
                    # Most likely could be a timeout to a spam message
                    comment.is_spam = True
            if not comment.is_spam:
                self.request.session["name"] = comment_f.cleaned_data['name']
                self.request.session["email"] = comment_f.cleaned_data['email']
                self.request.session["url"] = comment_f.cleaned_data['url']
            comment.save()
            return HttpResponseRedirect('#comment-%s' % comment.pk)
        context.update({'comment_form': comment_f})
        return self.render_to_response(context)


details = DetailsView.as_view()


class TagDetails(generic.ListView):
    template_name = 'blogango/tag_details.html'
    context_object_name = 'entries'

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug= self.kwargs['tag_slug'])
        self.kwargs['tag'] = tag
        tagged_entries = BlogEntry.objects.filter(is_published=True, tags__in=[tag])
        return tagged_entries

    def get_paginate_by(self, queryset):
        paginate_by = Blog.objects.get_blog().entries_per_page
        return paginate_by

    def get_context_data(self, *args, **kwargs):
        context = super(TagDetails, self).get_context_data(**kwargs)
        context['tag'] = self.kwargs['tag']
        return context

tag_details = TagDetails.as_view()

class InstallBlog(generic.TemplateView):
    template_name = 'blogango/install.html'

    def get(self, request, *args, **kwargs):
        if _is_blog_installed():
            return HttpResponseRedirect(reverse('blogango_index'))
        return super(InstallBlog, self).get(request, *args, **kwargs)

install_blog = InstallBlog.as_view()

class CreateBlogRoll(LoginRequiredMixin, generic.edit.FormView):
    template_name = 'blogango/blogroll.html'
    form_class = bforms.BlogForm
    success_url = reverse_lazy('blogango_blogroll')

    def get_context_data(self, *args, **kwargs):
        context = super(CreateBlogRoll, self).get_context_data(**kwargs)
        # our template expects context 'blogroll_form'
        context['blogroll_form'] = context['form']
        return context

    def form_valid(self, form):
        form.save()
        return super(CreateBlogRoll, self).form_valid(form)


create_blogroll = CreateBlogRoll.as_view()

class AuthorView(generic.ListView):
    template_name = 'blogango/author.html'
    context_object_name = 'entries'

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        self.kwargs['author'] = author
        author_posts = author.blogentry_set.filter(is_published=True)
        return author_posts

    def get_paginate_by(self, queryset):
        paginate_by = Blog.objects.get_blog().entries_per_page
        return paginate_by

    def get_context_data(self, *args, **kwargs):
        context = super(AuthorView, self).get_context_data(**kwargs)
        context['author'] = self.kwargs['author']
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
