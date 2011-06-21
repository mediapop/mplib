
import facebook
import urllib
import logging

from django.conf import settings
from django.db import IntegrityError

from helpers import ip_address
from models import FacebookUser, FacebookUserIP

# Find a JSON parser
try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)



from sentry.client.handlers import SentryHandler
logger = logging.getLogger(__name__)

is_logging_setup = False

if not is_logging_setup:
    is_logging_setup = True
    
    logger.setLevel(settings.LOGGING_LEVEL)
    logger.addHandler(SentryHandler())



class FacebookHelper(object):
    def __init__(self, request, 
                 allow_cookie_auth = False, 
                 facebook_app_secret = None, 
                 facebook_app_id = None,
                 cookie = None):
        """
        The xxxHandler classes in the AppEngine example are something like
        class-based views in Django. But it's difficult to do class-based views
        in a thread-safe way, so it's cleaner and simpler just to instantiate
        this helper class from within regular views.
        """
        self.request = request
        self.allow_cookie_auth = allow_cookie_auth
        
        if facebook_app_secret:
            self.facebook_app_secret = str(facebook_app_secret)
        else:
            self.facebook_app_secret = settings.FACEBOOK_APP_SECRET
            
        if facebook_app_id:
            self.facebook_app_id = str(facebook_app_id)
        else:
            self.facebook_app_id = settings.FACEBOOK_APP_ID
            
        self.cookie = cookie
    
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        """Returns the active user, or None if the user has not logged in."""
        if not hasattr(self, "_current_user"):
                      
            self._current_user = None
            
            if self.cookie:
                cookie = self.cookie
            else:
                cookie = self.parse_auth()
            
            if cookie:
#                print ('we have cookie', cookie["uid"])
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                try:
                    user = FacebookUser.objects.get(uid=cookie["uid"])
                except FacebookUser.DoesNotExist:
                    try:
                        graph = facebook.GraphAPI(cookie["access_token"])
                        
                        attempt_counter = 0
                        ATTEMPT_LIMIT = 10
                        
                        while attempt_counter < ATTEMPT_LIMIT:
                            try:                        
                                profile = graph.get_object("me")
                                break
                            except (IOError) as e:
                                attempt_counter += 1
                                
                                if attempt_counter == ATTEMPT_LIMIT:
                                    raise
                                
                                logger.info('mplib.current_user', extra = {
                                    'data': { 'exception': e }
                                })
                            
                    except facebook.GraphAPIError:
                        user = None
                    else:                        
                        user = FacebookUser(pk=str(profile["id"]),
                                            first_name=profile.get("first_name"),
                                            last_name=profile.get("last_name"),
                                            locale=profile.get("locale"),
                                            gender=profile.get("gender", ''),
                                            time_zone=profile.get('timezone', ''),
                                            email=profile.get('email', ''),
                                            access_token=cookie["access_token"])
                        
                        try:
                            user.save()
                        except IntegrityError as e:                            
                            logger.info('IntegrityError saving user', extra = {
                                    'data': { 'exception': e, 'profile': profile }
                                })

                            # this user has already been saved somehow, let's skip
                            # over this problem and grab him from the db
                            user = FacebookUser.objects.get(pk=str(profile["id"]))
                            
                        
                        ip = FacebookUserIP()
                        
                        ip.fb_user = user
                        ip.ip_address = ip_address(self.request)
                        
                        ip.save()
                        
                        
                else:
                    if user.access_token != cookie["access_token"]:
                        user.access_token = cookie["access_token"]
                        
                        ip = FacebookUserIP()
                        
                        ip.fb_user = user
                        ip.ip_address = ip_address(self.request)
                        
                        ip.save()
                        user.save()
                        
                self._current_user = user
        return self._current_user

    @property
    def graph(self):
        """Returns a Graph API client for the current user."""
        if not hasattr(self, "_graph"):
            if self.current_user:
                self._graph = facebook.GraphAPI(self.current_user.access_token)
            else:
                self._graph = facebook.GraphAPI()
        return self._graph

    @property
    def classic(self):
        """Returns a Graph API client for the current user."""
        if not hasattr(self, "_classic"):
            if self.current_user:
                self._classic = ClassicAPI(self.current_user.access_token)
            else:
                self._classic = ClassicAPI()
        return self._classic




    def parse_auth(self):
        """
        looks for a request param or cookie in order to decode a facebook object
        
        the returned value can then be used to do something like:
        
            graph = facebook.GraphAPI(cookie["access_token"])
            profile = graph.get_object("me")
            
        """
        signed_request = self.request.REQUEST.get('signed_request', None)
                
        if signed_request:
            signed_request = decode_signed_request(signed_request, self.facebook_app_secret)
           
            if signed_request and 'uid' in signed_request:
                return signed_request
                
        else:
            if self.allow_cookie_auth:
                return facebook.get_user_from_cookie(
                    self.request.COOKIES, self.facebook_app_id, self.facebook_app_secret)
    
        return None
    
    def is_fan(self, page_uid):
        return self.classic.request('method/pages.isfan', args = { 'page_id': page_uid, 'format': 'json' })
    
    def is_admin(self, page_uid):
        return self.classic.request('method/pages.isadmin', args = { 'page_id': page_uid, 'format': 'json' })
        
    def fql(self, query):
        return self.classic.request('method/fql.query', args = { 'query': query, 'format': 'json' })
    
    def has_app_added(self):
        print ('checking if app is added')
        return self.classic.request('method/users.isAppUser', args = { 'format': 'json' })
  
    def has_app_permission(self, permission):
        print ('checking if app permission is added')
        return self.classic.request('method/users.hasAppPermission', args = { 'format': 'json', 'ext_perm': permission })
  
def decode_signed_request(signed_request, secret):
    """
    http://developers.facebook.com/docs/authentication/canvas
    """
    import hmac, base64, hashlib
    
    if not signed_request:
        return None
    
    # watch out for split returning a non-correct number of elements
    try:
        sig, payload = map(str, signed_request.split('.', 1))
    except ValueError:
        return None
    
    def pad(string):
        if len(string) % 4:
            return string + '=' * (4 - len(string) % 4)
        return string
      
    try:
        sig = base64.urlsafe_b64decode(pad(sig))
        data = base64.urlsafe_b64decode(pad(payload))
        data = _parse_json(data)
    except:
        return None
    
    if data['algorithm'] != 'HMAC-SHA256':
        return None
    
    digest = hmac.new(secret, payload, hashlib.sha256).digest()
    
    if str(digest) != sig:
        return None
    
    classic =  {
        'access_token': data.get('oauth_token', None),
        'expires': data.get('expires', None) or None,
        'uid': data.get('user_id', None),
        'session_key': None,
    }

    return dict(data, **classic)
        
class ClassicAPI(object):
    def __init__(self, access_token=None):
        self.access_token = access_token
        
    def request(self, path, args=None, post_args=None):
        """Fetches the given path in the Graph API.

        We translate args to a valid query string. If post_args is given,
        we send a POST request to the given path with the given arguments.
        """
        if not args: args = {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)

        # we had some issues where the facebook server would hang up
        # on us while we are trying to authenticate the request, here
        # we try and attempt to loop a couple of times in case it's an
        # intermittent issue. 
        # IOError: ('http protocol error', 0, 'got a bad status line', None)
        
        ATTEMPT_LIMIT = 3
        attempt = 0
        
        while attempt < ATTEMPT_LIMIT:
            try:
                file = urllib.urlopen("https://api.facebook.com/" + path + "?" +
                              urllib.urlencode(args), post_data)
                
                break
            except (IOError) as e:
                attempt += 1
                                
                logger.debug('ClassicAPI.request IOException', extra = {
                    'data': { 'exception': e, 'attempt': attempt }
                })
    
                if attempt == ATTEMPT_LIMIT:
                    raise
                
        
                              
        try:
            response = file.read()
            try:
                response = _parse_json(response)
                
                try:
                    if response.get("error_code"):
                        print (response)
                        raise facebook.GraphAPIError(response["error_code"],
                                            response["error_msg"])
                except AttributeError:
                    # not json, possibly a single value, live with it...
                    pass
            except ValueError:
                # not json, possibly a single value, live with it...
                pass
                
        finally:
            file.close()
            
        return response

