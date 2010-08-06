
from datetime import date, datetime, time
from time import strptime

from django.core.urlresolvers import reverse
from django.db.models import signals

from pingback import register_pingback, ping_func
from pingback.client import ping_external_links, ping_directories
from django_xmlrpc import xmlrpcdispatcher

from blogango.models import BlogEntry

def pingback_blog_handler(year, month, slug, **kwargs):
    return BlogEntry.objects.get(created_on__year=year, 
                                 created_on__month=month, 
                                 slug=slug, 
                                 is_published=True)
    

# ping_details = {'blogango_details': pingback_blog_handler}

register_pingback('blogango.views.details', pingback_blog_handler)

xmlrpcdispatcher.register_function(ping_func, 'pingback.ping')

# ping external links in the entry

def get_blog_text(instance):
    return instance.text.rendered

signals.post_save.connect(ping_external_links(content_func=get_blog_text, url_attr='get_absolute_url'), sender=BlogEntry, weak=False)