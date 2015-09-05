# __author__ = 'naman'

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render
from social.exceptions import AuthForbidden
    
class MyMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthForbidden:
            return render(request, "jobport/needlogin.html", {})