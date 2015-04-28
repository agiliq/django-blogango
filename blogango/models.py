from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from taggit.managers import TaggableManager
from markupfield.fields import MarkupField
from markupfield.markup import DEFAULT_MARKUP_TYPES


class BlogManager(models.Manager):
    def get_blog(self):
        blogs = self.all()
        if blogs:
            return blogs[0]
        return None


class Blog(models.Model):
    """Blog wide settings.
     title:title of the Blog.
     tag_line: Tagline/subtitle of the blog.
               This two are genearlly displayed on each page's header.
     entries_per_page=Number of entries to display on each page.
     recents: Number of recent entries to display in the sidebar.
     recent_comments: Number of recent comments to display in the sidebar.
    """

    title = models.CharField(max_length=100)
    tag_line = models.CharField(max_length=100)
    entries_per_page = models.IntegerField(default=10)
    recents = models.IntegerField(default=5)
    recent_comments = models.IntegerField(default=5)

    objects = BlogManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):

        """There should not be more than one Blog object"""
        if Blog.objects.count() == 1 and not self.id:
            raise Exception("Only one blog object allowed.")
        # Call the "real" save() method.
        super(Blog, self).save(*args, **kwargs)


class BlogPublishedManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(BlogPublishedManager, self).get_queryset().filter(
            is_published=True,
            publish_date__lte=datetime.now())


class BlogEntry(models.Model):
    """Each blog entry.
    Title: Post title.
    Slug: Post slug.
          These two if not given are inferred directly from entry text.
    text = The main data for the post.
    summary = The summary for the text. probably can be derived from text,
              but we dont want do do that each time main page is displayed.
    created_on = The date this entry was created. Defaults to now.
    Created by: The user who wrote this.
    is_page: Is this a page or a post? Pages are the more important posts,
             which might be displayed differently. Defaults to false.
    is_published: Is this page published.
                  If yes then we would display this on site, otherwise no.
                  Defaults to true.
    comments_allowed: Are comments allowed on this post? Defaults to True
    is_rte: Was this post done using a Rich text editor?"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    text = MarkupField(default_markup_type=getattr(settings,
                                                   'DEFAULT_MARKUP_TYPE',
                                                   'plain'),
                       markup_choices=getattr(settings, "MARKUP_RENDERERS",
                                              DEFAULT_MARKUP_TYPES))
    summary = models.TextField()
    created_on = models.DateTimeField(default=datetime.max, editable=False)
    created_by = models.ForeignKey(User, unique=False)
    is_page = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    publish_date = models.DateTimeField(null=True)
    comments_allowed = models.BooleanField(default=True)
    is_rte = models.BooleanField(default=False)

    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    tags = TaggableManager()

    default = models.Manager()
    objects = BlogPublishedManager()

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Blog entries'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title is None or self.title == '':
            self.title = _infer_title_or_slug(self.text.raw)

        if self.slug is None or self.slug == '':
            self.slug = slugify(self.title)

        i = 1
        while True:
            created_slug = self.create_slug(self.slug, i)
            slug_count = BlogEntry.objects.filter(slug__exact=created_slug).exclude(pk=self.pk)
            if not slug_count:
                break
            i += 1
        self.slug = created_slug

        if not self.summary:
            self.summary = _generate_summary(self.text.raw)
        if not self.meta_keywords:
            self.meta_keywords = self.summary
        if not self.meta_description:
            self.meta_description = self.summary

        if self.is_published:
            #default value for created_on is datetime.max whose year is 9999
            if self.created_on.year == 9999:
                self.created_on = self.publish_date
        # Call the "real" save() method.
        super(BlogEntry, self).save(*args, **kwargs)

    def create_slug(self, initial_slug, i=1):
        if not i == 1:
            initial_slug += "-%s" % (i,)
        return initial_slug

    def get_absolute_url(self):
        return reverse('blogango_details',
                       kwargs={'year': self.created_on.strftime('%Y'),
                               'month': self.created_on.strftime('%m'),
                               'slug': self.slug})

    def get_edit_url(self):
        return reverse('blogango_admin_entry_edit', args=[self.id])

    def get_num_comments(self):
        cmnt_count = Comment.objects.filter(comment_for=self, is_spam=False).count()
        return cmnt_count

    def get_num_reactions(self):
        reaction_count = Reaction.objects.filter(comment_for=self).count()
        return reaction_count

    # check if the blog have any comments in the last 24 hrs.
    def has_recent_comments(self):
        yesterday = datetime.now()-timedelta(days=1)
        return Comment.objects.filter(
            comment_for=self, is_spam=False, created_on__gt=yesterday
        ).exists()

    # return comments in the last 24 hrs
    def get_recent_comments(self):
        yesterday = datetime.now()-timedelta(days=1)
        cmnts = Comment.objects.filter(
            comment_for=self, is_spam=False, created_on__gt=yesterday
        ).order_by('-created_on')
        return cmnts


class CommentManager(models.Manager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset().filter(is_public=True)


class BaseComment(models.Model):
    text = models.TextField()
    comment_for = models.ForeignKey(BlogEntry)
    created_on = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=100)
    user_url = models.URLField()

    class Meta:
        ordering = ['created_on']
        abstract = True

    def __unicode__(self):
        return self.text


class Comment(BaseComment):
    """Comments for each blog.
    text: The comment text.
    comment_for: the Post/Page this comment is created for.
    created_on: The date this comment was written on.
    created_by: THe user who wrote this comment.
    user_name = If created_by is null, this comment was by anonymous user.
                Name in that case.
    email_id: Email-id, as in user_name.
    is_spam: Is comment marked as spam?
             We do not display the comment in those cases.
    is_public: null for comments waiting to be approved, True if approved,
               False if rejected
    user_ip: Ip address from which this comment was made
    user_agent: User agent of the commenter
    """

    created_by = models.ForeignKey(User, unique=False, blank=True, null=True)
    email_id = models.EmailField()
    is_spam = models.BooleanField(default=False)
    is_public = models.NullBooleanField(null=True, blank=True)
    user_ip = models.IPAddressField(null=True)
    user_agent = models.CharField(max_length=200, default='')

    default = models.Manager()
    objects = CommentManager()

    def save(self, *args, **kwargs):
        if self.is_spam:
            self.is_public = False
        super(Comment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blogango_comment_details', args=[self.id, ])


class Reaction(BaseComment):
    """
    Reactions from various social media sites
    """
    reaction_id = models.CharField(max_length=200, primary_key=True)
    source = models.CharField(max_length=200)
    profile_image = models.URLField(blank=True, null=True)


class BlogRoll(models.Model):
    url = models.URLField(unique=True)
    text = models.CharField(max_length=100)
    is_published = models.BooleanField(default=True)

    def __unicode__(self):
        return self.text

    def get_absolute_url(self):
        return self.url


#Helper methods
def _infer_title_or_slug(text):
    return '-'.join(text.split()[:5])


def _generate_summary(text):
    return ' '.join(text.split()[:100])
