
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

from taggit.models import Tag

from blogango.views import _get_archive_months

register = template.Library()

class BlogangoContext(template.Node):
    def __init__(self):
        pass
    
    def render(self, context):
        tags = Tag.objects.all()
        feed_url = getattr(settings, 'FEED_URL', reverse('blogango_feed', args=['latest'])) 
        archive_months = _get_archive_months()
                
        extra_context = {'tags': tags, 
                'feed_url': feed_url,
                'archive_months': archive_months}
        context.update(extra_context)
        return ''
    
def blogango_extra_context(parser, token):
    return BlogangoContext()
    
register.tag('blogango_extra_context', blogango_extra_context)