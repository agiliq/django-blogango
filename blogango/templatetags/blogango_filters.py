import re

from django import template
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db.models import Count

from taggit.models import Tag, TaggedItem
from blogango.views import _get_archive_months
from blogango.models import Blog, BlogEntry

register = template.Library()

class BlogangoContext(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        #only one blog must be present
        blog = Blog.objects.get_blog()
        tags = Tag.objects.annotate(num_tagged_entries=Count('taggit_taggeditem_items')).filter(num_tagged_entries__gt=2)
        feed_url = reverse('blogango_feed')
        archive_months = _get_archive_months()
        site = Site.objects.get_current()

        extra_context = {
                         'tags': tags,
                         'feed_url': feed_url,
                         'archive_months': archive_months,
                         'blog': blog,
                         'site': site,
                         }
        context.update(extra_context)
        return ''

def blogango_extra_context(parser, token):
    return BlogangoContext()


@register.assignment_tag
def related_posts(post):
    tags = post.tags.all()
    blog_entry_ids = [each.content_object.id for each in TaggedItem.objects.filter(tag__in=tags)]
    related_posts = BlogEntry.objects.filter(id__in=blog_entry_ids,
                                             is_published=True).exclude(id=post.id).order_by('created_on')[:5]
    return set([el for el in related_posts])

#django snippets #2107
@register.filter(name='twitterize')
def twitterize(token):
    return re.sub(r'\W(@(\w+))', r'<a href="https://twitter.com/\2">\1</a>', token)
twitterize.is_safe = True

register.tag('blogango_extra_context', blogango_extra_context)

@register.filter
def truncate_chars(ip_string, length=30):
    length, dots = int(length), 3
    if len(ip_string) < length:return ip_string
    else:return ip_string[:length-dots] + '.' * dots
