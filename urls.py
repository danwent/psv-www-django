from django.conf.urls.defaults import *

from notary_web import views 

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('django.views.generic.simple',
    (r'^notary_query$', views.notary_query), 
    (r'^notary_svg/(.*)/(\d+)/(\d+).svg$', views.notary_svg)
    # Example:
    # (r'^notary_web/', include('notary_web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
