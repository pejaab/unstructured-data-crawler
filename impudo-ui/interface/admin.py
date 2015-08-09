from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db import models
from django.forms import TextInput, Textarea
from interface.models import Crawler, Record, Template
from import_export import resources
from import_export.admin import ExportActionModelAdmin

class AdminSite(admin.AdminSite):
    site_header = 'Manage Crawler'


class RecordResource(resources.ModelResource):

    class Meta:
        model = Record


class RecordAdmin(ExportActionModelAdmin):
    list_filter = (
            ('template_id', admin.RelatedOnlyFieldListFilter),
            )
    search_fields = ['title', 'result', 'template_id']
    list_display = ('title', 'result', 'template_id')

    resource_class = RecordResource


class CrawlerInline(admin.TabularInline):
    model = Crawler
    extra = 0
    exclude = ('url',)
    max_num = 0
    readonly_fields = ('xpath', 'content', 'crawled')


class TemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('url_abbr', 'url', 'desc')
    list_display = ('url_abbr', 'url', 'desc')


    inlines = [CrawlerInline,]

    def has_add_permission(self, request):
        return False


admin_site = AdminSite(name='admin')
admin_site.register(Template, TemplateAdmin)
admin_site.register(Record, RecordAdmin)
