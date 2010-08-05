from django.contrib import admin

from blogango.models import Blog, BlogEntry, Comment, BlogRoll, Reaction

class BlogEntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    
admin.site.register(Blog)
admin.site.register(BlogEntry, BlogEntryAdmin)
admin.site.register(Comment)
admin.site.register(BlogRoll)
admin.site.register(Reaction)