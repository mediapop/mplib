from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.core.mail import mail_admins
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.urlresolvers import reverse

import sys

from facebook_lib import FacebookHelper

def json_view(func):
    def wrap(request, *a, **kw):
        response = None
        try:
            response = func(request, *a, **kw)
            assert isinstance(response, dict)
            if 'result' not in response:
                response['result'] = 'ok'
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception, e:
            if settings.DEBUG:
                raise
            else:
                # Mail the admins with the error
                exc_info = sys.exc_info()
                subject = 'JSON view error: %s' % request.path
                
                try:
                    request_repr = repr(request)
                except:
                    request_repr = 'Request repr() unavailable'
                    
                import traceback
                message = 'Traceback:\n%s\n\nRequest:\n%s' % (
                    '\n'.join(traceback.format_exception(*exc_info)),
                    request_repr,
                    )
                mail_admins(subject, message, fail_silently = True)
    
                # Come what may, we're returning JSON.
                if hasattr(e, 'message'):
                    msg = e.message
                else:
                    msg = _('Internal error') + ': ' + str(e)
                response = {'result': 'error',
                            'text': msg}

        json = simplejson.dumps(response)
        
        print('json', json)
        
        return HttpResponse(json, mimetype='application/json')
    
    return wrap

def fb_login_required(allow_cookie_auth = False, 
                    facebook_app_secret = None, 
                    facebook_app_id = None):
    
    def wrap(f):
        def _decorator(request, *args, **kwargs):
    
            fb = FacebookHelper(request, 
                                allow_cookie_auth = allow_cookie_auth, 
                                facebook_app_secret = facebook_app_secret, 
                                facebook_app_id = facebook_app_id)
            
            if not fb.parse_auth:
                
                r = request.get_full_path()
                
                return HttpResponseRedirect(kwargs['auth_view'] + '?r=' + r)
            
            return f(request, *args, **kwargs)
        return _decorator
    return wrap

def fb_app_required(allow_cookie_auth = False, 
                    facebook_app_secret = None, 
                    facebook_app_id = None):
    
    def wrap(f):
        def _decorator(request, *args, **kwargs):
    
            fb = FacebookHelper(request, 
                                allow_cookie_auth = allow_cookie_auth, 
                                facebook_app_secret = facebook_app_secret, 
                                facebook_app_id = facebook_app_id)
            
            if not fb.has_app_added():
                
                return HttpResponseRedirect(reverse(kwargs['auth_view']))
            
            return f(request, *args, **kwargs)
        return _decorator
    return wrap


def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
