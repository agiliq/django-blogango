
from django.conf import settings
from django.core.urlresolvers import reverse

from taggit.models import Tag

from blogango.models import Blog, BlogRoll
from blogango.views import _get_archive_months

def extra_context(request):
    blog_rolls = BlogRoll.objects.filter(is_published=True)
    tags = Tag.objects.all()
    feed_url = getattr(settings, 'FEED_URL', reverse('blogango_feed', args=['latest'])) 
    
    archive_months = _get_archive_months()
    
    blog = Blog.objects.all()
    blog = blog[0] if blog.count() > 0 else None
    
    return {'blog': blog,
            'blog_rolls': blog_rolls,
            'tags': tags, 
            'canonical_url': request.build_absolute_uri(),
            'feed_url': feed_url,
            'pingback_xmlrpc_url': request.build_absolute_uri(reverse('xmlrpc')),
            'archive_months': archive_months}

