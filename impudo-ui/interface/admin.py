from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db import models
from django.forms import TextInput, Textarea
from interface.models import Crawler, Record, Template
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from interface.tasks import scrape


class AdminSite(admin.AdminSite):
    site_header = 'Manage Crawler'


class RecordResource(resources.ModelResource):

    class Meta:
        model = Record


class RecordAdmin(ExportActionModelAdmin):
    exclude = ('url',)
    readonly_fields = ('template',)
    fields = ('template', 'title', 'result')
    list_display = ('title', 'result', 'template')
    list_filter = (
            ('template', admin.RelatedOnlyFieldListFilter),
            )
    search_fields = ['template__id', 'template__url_abbr']

    resource_class = RecordResource
    

class CrawlerInline(admin.TabularInline):
    model = Crawler
    extra = 0
    exclude = ('url',)
    max_num = 0
    readonly_fields = ('xpath', 'content', 'crawled')


class TemplateAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'url_abbr', 'url', 'desc', 'img',)
    fields = ('id', 'url_abbr', 'url', 'img', 'desc')
    list_display = ('url_abbr', 'desc',)

    actions = ('dispatch_crawler',)
    inlines = [CrawlerInline,]

    def has_add_permission(self, request):
        return False

    def dispatch_crawler(self, request, queryset):
        for item in queryset:
            scrape.delay(item.id)
    dispatch_crawler.short_description = "Dispatch the crawler for this template"

admin_site = AdminSite(name='admin')
admin_site.register(Template, TemplateAdmin)
admin_site.register(Record, RecordAdmin)
