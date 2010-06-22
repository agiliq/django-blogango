from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change, password_reset
from django.contrib.sitemaps import GenericSitemap

from blogango import feeds
from blogango.models import BlogEntry

blog_info_dict = {
    'queryset': BlogEntry.objects.filter(is_published=True),
    'date_field': 'created_on',
}
sitemaps = {
    'blog': GenericSitemap(blog_info_dict, priority=0.5)
}

urlpatterns = patterns('blogango.views',
    url(r'^welcome/$', 'welcome', name='blogango_welcome'),
    url(r'^install/$', 'install_blog', name='blogango_install'),
    url(r'^preferences/$', 'edit_preferences', name='blogango_edit_preferences'),
     
    url(r'^$', 'index', name='blogango_index'),
    url(r'^page/(?P<page>\d+)/$', 'index',  name='blogango_page'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[-\w]+)/$', 'details', name='blogango_details'),
    url(r'^new/$', 'create_entry', name='blogango_create'),
    url(r'^blogroll/$', 'create_blogroll', name='blogango_blogroll'),
    url(r'^moderate/$', 'moderate_comments', name='blogango_mod_comments'),
    url(r'^entries/$', 'mod_entries', name='blogango_mod_entries'),
    url(r'^tag/(?P<tag_slug>\w+)/$','tag_details', name='blogango_tag_details'),
    url(r'^manage/$', 'manage', name='blogango_manage'),
    url(r'^edit/(?P<entry_id>\d+)/$', 'edit_entry', name='blogango_edit_entry'),
    url(r'^comment/(?P<comment_id>\d+)/$', 'comment_details', name='blogango_comment_details'),
    url(r'^author/(?P<username>[\w.@+-]+)/$', 'author', name='blogango_author'),
    
)

#search view
urlpatterns += patterns('blogango.search',
    url(r'^search/$', 'search', name = 'search'),        
)

# sitemap.xml
urlpatterns += patterns('django.contrib.sitemaps.views',
    url(r'^sitemap\.xml$', 'sitemap', {'sitemaps': sitemaps}),        
)     

# Archive view
urlpatterns += patterns('blogango.views',
    url(r'^archive/(?P<year>\d+)/(?P<month>\w+)/$', 'monthly_view', name='blogango_archives')
)

urlpatterns += patterns('django_xmlrpc.views',
    url(r'^xmlrpc/$', 'handle_xmlrpc', {}, name='xmlrpc'),
)

feeds = {'latest': feeds.main_feed, 'tag':feeds.CatFeed}
# feeds = {'latest': feeds.main_feed}
urlpatterns += patterns('',
    url(r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name='blogango_feed')
)
