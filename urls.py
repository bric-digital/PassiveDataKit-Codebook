from django.conf.urls import url

from .views import pdk_codebook_page, pdk_codebook_sitemap

urlpatterns = [
    url(r'^(?P<generator>.+)/$', pdk_codebook_page, name='pdk_codebook_page'),
    url(r'^sitemap.json$', pdk_codebook_sitemap, name='pdk_codebook_sitemap')
]
