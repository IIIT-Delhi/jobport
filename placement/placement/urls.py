# //=======================================================================
# // Copyright JobPort, IIIT Delhi 2015.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================




# __author__ = 'naman'

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

handler500 = "jobport.views.server_error"
handler404 = "jobport.views.not_found"

urlpatterns = patterns('',
	url('', include('jobport.urls')),
	url('', include('social.apps.django_app.urls', namespace='social')),
	url(r'^search/', include('haystack.urls')),
	url(r'^batcave/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
