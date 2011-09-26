from datetime import datetime
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change, password_reset
from django.contrib.sitemaps import GenericSitemap
from blogango import feeds
from blogango.models import BlogEntry

blog_info_dict = {
    'queryset': BlogEntry.objects.filter(is_published=True, publish_date__lte=datetime.now),
    'date_field': 'publish_date',
}
sitemaps = {
    'blog': GenericSitemap(blog_info_dict, priority=0.5)
}

urlpatterns = patterns('blogango.views',
    url(r'^$', 'index', name='blogango_index'),
    url(r'^install/$', 'install_blog', name='blogango_install'),
    url(r'^preferences/$', 'edit_preferences', name='blogango_edit_preferences'),
    url(r'^page/(?P<page>\d+)/$', 'index',  name='blogango_page'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[-\w]+)/$', 'details', name='blogango_details'),
    url(r'^new/$', 'create_entry', name='blogango_create'),
    url(r'^blogroll/$', 'create_blogroll', name='blogango_blogroll'),
    url(r'^moderate/$', 'moderate_comments', name='blogango_mod_comments'),
    url(r'^entries/$', 'mod_entries', name='blogango_mod_entries'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$','tag_details', name='blogango_tag_details'),
    url(r'^manage/$', 'manage', name='blogango_manage'),
    url(r'^edit/(?P<entry_id>\d+)/$', 'edit_entry', name='blogango_edit_entry'),
    url(r'^comment/(?P<comment_id>\d+)/$', 'comment_details', name='blogango_comment_details'),
    url(r'^author/(?P<username>[\w.@+-]+)/$', 'author', name='blogango_author'),

    url(r'^admin/$', 'admin_dashboard', name='blogango_admin_dashboard'),
    url(r'^admin/entry/new/$', 'admin_entry_edit', name='blogango_admin_entry_new'),
    url(r'^admin/entry/edit/(?P<entry_id>\d+)/$', 'admin_entry_edit', name='blogango_admin_entry_edit'),
    url(r'^admin/entry/manage/$', 'admin_manage_entries', name='blogango_admin_entry_manage'),
    url(r'^admin/comments/manage/$', 'admin_manage_comments', name='blogango_admin_comments_manage'),
    url(r'^admin/preferences/edit/$', 'admin_edit_preferences', name='blogango_admin_edit_preferences'),
    url(r'^admin/comment/approve/(?P<comment_id>\d+)/$', 'admin_comment_approve', name='blogango_admin_comment_approve'),
    url(r'^admin/comment/block/(?P<comment_id>\d+)/$', 'admin_comment_block', name='blogango_admin_comment_block'),
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

urlpatterns += patterns('blogango.views',
    url(r'^(?P<slug>[-\w]+)/$', 'page_details', name='blogango_page_details'),
)
