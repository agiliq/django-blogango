from datetime import datetime
from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.comments.moderation import CommentModerator, moderator
from django.template.defaultfilters import slugify

from taggit.managers import TaggableManager
from markupfield.fields import MarkupField
from markupfield.markup import DEFAULT_MARKUP_TYPES

class Blog(models.Model):
    """Blog wide settings.
     title:title of the Blog.
     tag_line: Tagline/subtitle of the blog. This two are genearlly displayed on each page's header.
     entries_per_page=Number of entries to display on each page.
     recents: Number of recent entries to display in the sidebar.
     recent_comments: Number of recent comments to display in the sidebar.
    """

    title = models.CharField(max_length=100)
    tag_line = models.CharField(max_length=100)
    entries_per_page = models.IntegerField(default=10)
    recents = models.IntegerField(default=5)
    recent_comments = models.IntegerField(default=5)

    def __unicode__(self):
        return self.title

    def save(self):

        """There should not be more than one Blog object"""
        if Blog.objects.count() > 1 and self.id:
            raise Exception("Only one blog object allowed.")
        super(Blog, self).save() # Call the "real" save() method.

    @staticmethod
    def is_installed():
        if Blog.objects.count() == 0:
            return False
        return True

class BlogPublishedManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(BlogPublishedManager, self).get_query_set().filter(is_published=True,
                publish_date__lte=datetime.now())

class BlogEntry(models.Model):
    """Each blog entry.
    Title: Post title.
    Slug: Post slug. These two if not given are inferred directly from entry text.
    text = The main data for the post.
    summary = The summary for the text. probably can can be derived from text, bit we dont want do do that each time main page is displayed.
    created_on = The date this entry was created. Defaults to now.
    Created by: The user who wrote this.
    is_page: IS this a page or a post? Pages are the more important posts, which might be displayed differently. Defaults to false.
    is_published: Is this page published. If yes then we would display this on site, otherwise no. Default to true.
    comments_allowed: Are comments allowed on this post? Default to True
    is_rte: Was this post done using a Rich text editor?"""

    title = models.CharField(max_length=100)
    slug = models.SlugField()
    text = MarkupField(default_markup_type=getattr(settings,
                                                   'DEFAULT_MARKUP_TYPE',
                                                   'plain'),
                       markup_choices=getattr(settings, "MARKUP_RENDERERS",
                                              DEFAULT_MARKUP_TYPES))
    summary = models.TextField()
    created_on = models.DateTimeField(default=datetime.max)
    created_by = models.ForeignKey(User, unique=False)
    is_page = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    publish_date = models.DateTimeField()
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
        if self.title == None  or self.title == '':
            self.title = _infer_title_or_slug(self.text.raw)

        if self.slug == None or self.slug == '':
            self.slug = slugify(self.title)

        slug_count = BlogEntry.objects.filter(slug__startswith=self.slug).exclude(pk=self.pk).count()
        if slug_count:
            self.slug += '-%s' %(slug_count + 1)

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
        super(BlogEntry, self).save() # Call the "real" save() method.

    @permalink
    def get_absolute_url(self):
        return ('blogango_details', (), {'year': self.created_on.strftime('%Y'),
                                         'month': self.created_on.strftime('%m'),
                                         'slug': self.slug})

    @permalink
    def get_edit_url(self):
        return ('blogango.views.admin_entry_edit', [self.id])

    def get_num_comments(self):
        cmnt_count = Comment.objects.filter(comment_for=self, is_spam=False).count()
        return cmnt_count

    def get_num_reactions(self):
        reaction_count = Reaction.objects.filter(comment_for=self).count()
        return reaction_count

class CommentManager(models.Manager):
    def get_query_set(self):
        return super(CommentManager, self).get_query_set().filter(is_public=True)

class BaseComment(models.Model):
    text = models.TextField()
    comment_for = models.ForeignKey(BlogEntry)
    created_on = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=100)
    user_url = models.CharField(max_length=100)

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
    user_name = If created_by is null, this comment was by anonymous user. Name in that case.
    email_id: Email-id, as in user_name.
    is_spam: Is comment marked as spam? We do not display the comment in those cases.
    is_public: null for comments waiting to be approved, True if approved, False if rejected
    """

    created_by = models.ForeignKey(User, unique=False, blank=True, null=True)
    email_id = models.EmailField()
    is_spam = models.BooleanField(default=False)
    is_public = models.NullBooleanField(null=True, blank=True)

    default = models.Manager()
    objects = CommentManager()

    @permalink
    def get_absolute_url (self):
        return ('comment_details', self.id)

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

class CommentModerator(CommentModerator):
    email_notification = True
    enable_field = 'is_public'

#Helper methods
def _infer_title_or_slug(text):
    return '-'.join(text.split()[:5])

def _generate_summary(text):
    return ' '.join(text.split()[:100])

moderator.register(Comment, CommentModerator)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^markupfield\.fields\.MarkupField"])

