from django.conf.urls import url

from . import apis

urlpatterns = [
    url(r'^signup/$', apis.MySocialView.as_view(), name="social-signup"),
]