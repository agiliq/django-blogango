
from datetime import date, datetime, time
from time import strptime

from django.core.urlresolvers import reverse
from django.db.models import signals

from pingback import create_ping_func
from pingback.client import ping_external_links, ping_directories
from django_xmlrpc import xmlrpcdispatcher

from blogango.models import BlogEntry

def pingback_blog_handler(year, month, slug, **kwargs):
    return BlogEntry.objects.get(created_on__year=year, 
                                 created_on__month=month, 
                                 slug=slug, 
                                 is_published=True)
    

ping_details = {'blogango_details': pingback_blog_handler}

ping_func = create_ping_func(**ping_details)

xmlrpcdispatcher.register_function(ping_func, 'pingback.ping')

signals.post_save.connect(ping_external_links(content_attr='text', url_attr='get_absolute_url'), sender=BlogEntry, weak=False)

