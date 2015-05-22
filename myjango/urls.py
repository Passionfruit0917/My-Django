from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from app.views import *
from alert.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
     url(r'^app/cn$', cn),
     url(r'^app/eu$', eu),
     url(r'^app/ga$', ga),
     url(r'^app/wm$', wm),
     url(r'^cn_aj_res/$', cn_aj_res),
     url(r'^eu_aj_res/$', eu_aj_res),
     url(r'^ga_aj_res/$', ga_aj_res),
     url(r'^eu_daily_sla/$', eu_daily_sla), 
     url(r'^cn_dq_chart/$', cn_dq_chart),
     url(r'^cn_dq/$', cn_dq),
     url(r'^alert/$', alert),
     url(r'^ga_daily_sla/$', ga_daily_sla),
     url(r'^ajax_response/$',ajax_response),
     url(r'^daily_sla/$',daily_sla),
     url(r'^submitstatus/$',submitstatus),
     url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
     url(r'^task/$',taskview),
     url(r'^shift_filter/$',shift_filter),
     url(r'^app/$',welcome),
     
)
