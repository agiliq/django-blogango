from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    ('^admin/', include(admin.site.urls)),
    (r'^', include('blogango.urls')),
)

if settings.DEBUG:    
    urlpatterns += patterns('',
        url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
