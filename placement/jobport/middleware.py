from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.conf.urls import url
from django.contrib.auth.models import User
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render
from social.exceptions import AuthForbidden
from django.core.urlresolvers import resolve
from urlparse import urlparse
import re

#class CvControlMiddleware(object):
 #   def process_request(self,request):
  #      current_url = request.get_full_path()
   #     geturl = urlparse(current_url)
    #    name = request.user.username.split('@')[0].lower()
     #   if name != geturl.path.split('/')[-1].split('.')[0].split('_')[0].lower():
      #      return render(request, "jobport/notallowed.html")

    
class MyMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthForbidden:
            return render(request, "jobport/needlogin.html", {})

#    def process_request(self,request):
#        if request.user.is_authenticated():
#            name = request.user.username.split('@')[0]
#            roll=[]
#            for i in name:
#                if i.isdigit():
#                    roll.append(i)
#
#            if len(roll) == 5:
#                if int(roll[1])>1 or int(roll[1])<1:
#                    auth_logout(request)
#                    return render(request,"jobport/notlogin.html",{})
#            elif len(roll) == 4:
#                if int(roll[1])>3 or int(roll[1])<3:
#                    auth_logout(request)
#                    return render(request,"jobport/notlogin.html",{})

#    def process_request(self,request):
        
