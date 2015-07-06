from django.contrib import admin
from django.contrib.auth.models import Group, User

from interface.models import Template, Crawler

admin.site.unregister(User)
admin.site.unregister(Group)

class CrawlerInline(admin.TabularInline):
    model = Crawler
    extra = 0
    exclude = ('url', 'active')
    max_num = 0
    readonly_fields = ('xpath', 'content', 'crawled')


class TemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('url_abbr', 'url', 'desc')
    list_display = ('url_abbr', 'url', 'desc')

    inlines = [CrawlerInline]

    def has_add_permission(self, request):
        return False

#class CrawlerAdmin(admin.ModelAdmin):

#    def has_add_permission(self, request):
#        return False

admin.site.register(Template, TemplateAdmin)
#admin.site.register(Crawler, CrawlerAdmin)
