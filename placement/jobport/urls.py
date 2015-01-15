from django.conf.urls import patterns, url

from . import views


handler404 = 'views.my_404_view'

urlpatterns = patterns('',
	url(r'^$', views.home, name='home'),
	url(r'^logout/$', views.logout, name='logout'),
	url(r'^needlogin/$', views.needlogin, name='needlogin'),
	url(r'^newuser/$', views.newuser, name='newuser'),
	url(r'^openjob/$', views.openjob, name='openjob'),
	url(r'^profile/$', views.profile, name='profile'),
	url(r'^stats/$', views.stats, name='stats'),
	url(r'^uploadcgpa/$', views.uploadcgpa, name='uploadcgpa'),
	url(r'^students/(?P<studentid>.*)/edit/$', views.admineditstudent, name='admineditstudent'),
	url(r'^job/(?P<jobid>\d+)/$', views.jobpage, name='jobpage'),
	url(r'^job/(?P<jobid>\d+)/apply/$', views.jobapply, name='jobapply'),
	url(r'^job/(?P<jobid>\d+)/withdraw/$', views.jobwithdraw, name='jobwithdraw'),
	url(r'^job/(?P<jobid>\d+)/edit/$', views.jobedit, name='jobedit'),
	url(r'^job/(?P<jobid>\d+)/delete/$', views.jobdelete, name='jobdelete'),
	url(r'^job/(?P<jobid>\d+)/sendselectedemail/$', views.sendselectedemail, name='sendselectedemail'),
	url(r'^job/(?P<jobid>\d+)/applicants/$', views.jobapplicants, name='jobapplicants'),
	url(r'^job/(?P<jobid>\d+)/getresume/$', views.getresumes, name='jobgetresumes'),
	url(r'^job/(?P<jobid>\d+)/getcsv/$', views.getjobcsv, name='jobgetcsvs'),
	url(r'^job/(?P<jobid>\d+)/selections/$', views.adminjobselected, name='adminjobselected'),
	url(r'^myapplications/$', views.myapplications, name='myapplications'),
	url(r'^batches/$',views.viewbatches,name='viewbatches'),
	url(r'^openbatch/$', views.batchcreate, name='openbatch'),
	url(r'^batch/(?P<batchid>\d+)/$',views.batchpage,name='batchpage'),
	url(r'^batch/(?P<batchid>\d+)/delete/$',views.batchdestroy,name='batchdestroy'),
	url(r'^batch/(?P<batchid>\d+)/edit/$',views.batchedit,name='batchedit'),
	url(r'^batch/(?P<batchid>\d+)/getbatchlist/$',views.getbatchlist,name='getbatchlist'),
	url(r'^batch/(?P<batchid>\d+)/addstudentstobatch/$',views.uploadstudentsinbatch,name='uploadstudentsinbatch'),
	url(r'^batch/(?P<batchid>\d+)/getbatchresume/$',views.getbatchresumes,name='getbatchresumes'),
	url(r'^feedback/$', views.feedback, name='feedback'),
	url(r'^extraStuff/$', views.blockedUnplacedlist, name='blockedUnplacedlist'),
	url(r'files/resume/(.+)',views.fileview,name='fileview'),
	url(r'search/results/$',views.search,name='search'),
	url(r'material.min.js.map$',views.test,name='test'),

)
