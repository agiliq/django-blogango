from django.contrib import admin

from pingback.models import Pingback, PingbackClient, DirectoryPing


class PingbackAdmin(admin.ModelAdmin):
    list_display = ('url', 'admin_object', 'date', 'approved', 'title')

admin.site.register(Pingback, PingbackAdmin)

class PingbackClientAdmin(admin.ModelAdmin):
    list_display = ('admin_object', 'url', 'date', 'success')

admin.site.register(PingbackClient, PingbackClientAdmin)

class DirectoryPingAdmin(admin.ModelAdmin):
    list_display = ('url', 'date', 'success')

admin.site.register(DirectoryPing, DirectoryPingAdmin)
