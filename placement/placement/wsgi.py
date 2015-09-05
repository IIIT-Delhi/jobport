# //=======================================================================
# // Copyright JobPort, IIIT Delhi 2015.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================




# __author__ = 'naman'


"""
WSGI config for placement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "placement.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
