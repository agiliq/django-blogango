from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

import os

dirname = os.path.dirname(globals()["__file__"])


admin.autodiscover()


urlpatterns = patterns('',

    ('^admin/(.*)', admin.site.root),

    (r'^', include('blogango.urls')),
    (r'^accounts/', include('registration.urls')),
    
)

if settings.DEBUG:    
    media_dir = os.path.join(dirname, 'site_media')
    urlpatterns += patterns('',
            url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_dir}),
        )
