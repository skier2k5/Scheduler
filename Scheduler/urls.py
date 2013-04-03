from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from Scheduler import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'Scheduler.views.test'),
    url(r'^$', 'Scheduler.views.index'),
    url(r'^ajax/getcourses/(?P<deptID>\d*)$','Scheduler.views.getCourses'),
    url(r'^ajax/getsinglecourse/(?P<courseID>\w*\s*\d*)/(?P<courseName>.*)$','Scheduler.views.getSingleCourse'),
    url(r'^ajax/getsingleclass/(?P<callNum>\d*)$','Scheduler.views.getSingleClass'),
    url(r'^ajax/courses/$','Scheduler.views.createSchedule'),
    url(r'^ajax/saveclasses/$','Scheduler.views.saveClasses'),
    url(r'^ajax/addclassestosched/$','Scheduler.views.addClassesToSched'),
    url(r'^ajax/removeclassfromsched/$','Scheduler.views.removeClassFromSched'),
    url(r'^ajax/searchclasses/$','Scheduler.views.searchClasses'),
    url(r'^printsched/$','Scheduler.views.printSched'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':settings.STATIC_ROOT}),
    url(r'^ajax/checkuser/(?P<username>.*)$','Scheduler.views.checkUser'),
    url(r'^ajax/checkemail/(?P<email>.*)$','Scheduler.views.checkEmail'),
    url(r'^ajax/reguser$','Scheduler.views.regUser'),
    url(r'^ajax/login$','Scheduler.views.login'),
    url(r'^ajax/addpe$','Scheduler.views.addPe'),
    url(r'^ajax/removepe$','Scheduler.views.removePe'),
    url(r'^ajax/addclass$','Scheduler.views.addClass'),
    url(r'^ajax/removeclass$','Scheduler.views.removeClass'),
    url(r'^ajax/setprefs$','Scheduler.views.setPrefs'),
    url(r'^ajax/getclassinfo$','Scheduler.views.getClassesInfo'),
    url(r'^ajax/getprefs$', 'Scheduler.views.getPrefs'),
    url(r'^ajax/getpersevents$', 'Scheduler.views.getPersEvents'),
    url(r'^logout$','Scheduler.views.logout'),
    url(r'^clearsession$','Scheduler.views.clearSession'),
    url(r'^checksession$','Scheduler.views.checkSession'),
    # url(r'^Scheduler/', include('Scheduler.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
