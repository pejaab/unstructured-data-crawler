from django.conf.urls import url
from interface import views

urlpatterns = [
    url(r'^new$', views.new_template, name='new_template'),
    url(r'^(\d+)/$', views.view_template, name='view_template'),
        ]
