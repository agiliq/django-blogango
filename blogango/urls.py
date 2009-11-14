from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change, password_reset

from blogango import feeds

urlpatterns = patterns('blogango.views',
     url(r'^welcome/$', 'welcome', name='blogango_welcome'),
     url(r'^install/$', 'install_blog', name = 'blogango_install'),
     url(r'^preferences/$', 'edit_preferences', name = 'blogango_edit_preferences'),
     url(r'^$', 'index', name = 'blogango_index'),
     url(r'^page/(?P<page>\d+)/$', 'index',  name = 'blogango_page'),
     url(r'^details/(?P<entry_id>\d+)/$', 'details', name = 'blogango_details'),
     url(r'^new/$', 'create_entry', name = 'blogango_create'),
     url(r'^blogroll/$', 'create_blogroll', name = 'blogango_blogroll'),
     url(r'^moderate/$', 'moderate_comments', name = 'blogango_mod_comments'),
     url(r'^entries/$', 'mod_entries', name = 'blogango_mod_entries'),
     url(r'^tag/(?P<tag_txt>\w+)/$','tag_details', name = 'blogango_tag_details'),
     url(r'^manage/$', 'manage', name = 'blogango_manage'),
     url(r'^edit/(?P<entry_id>\d+)/$', 'edit_entry', name = 'blogango_edit_entry'),
     url(r'^comment/(?P<comment_id>\d+)/$', 'comment_details', name = 'blogango_comment_details'),

)

#search view
urlpatterns += patterns('blogango.search',
      url(r'^search/$', 'search', name = 'search'),        
    )
     

# Archive view
urlpatterns += patterns('blogango.views',
        (r'^archive/(?P<year>\d+)/(?P<month>\w+)/$', 'monthly_view',)
    )


feeds = {'latest': feeds.main_feed, 'tag':feeds.CatFeed}

urlpatterns += patterns('',
      (r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds})
      )
