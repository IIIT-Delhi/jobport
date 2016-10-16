# //=======================================================================
# // Copyright JobPort, IIIT Delhi 2015.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

from django.shortcuts import render
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social.exceptions import AuthForbidden


class MyMiddleware(SocialAuthExceptionMiddleware):

    def process_exception(self, request, exception):
        if type(exception) == AuthForbidden:
            return render(request, "jobport/needlogin.html", {})
