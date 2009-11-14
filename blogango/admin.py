from django.contrib import admin

from blogango.models import Blog, BlogEntry, Comment, Tag, BlogRoll

admin.site.register(Blog)
admin.site.register(BlogEntry)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(BlogRoll)