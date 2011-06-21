from django.conf import settings # import the settings file

import datetime

from helpers import ip_address
    
def media_url(request):

    media_url = settings.MEDIA_URL
    
    if request.is_secure() and getattr(settings, 'HTTPS_SUPPORT', True): 
        media_url = settings.MEDIA_URL.replace('http://', 'https://') 
    
    
    return {
        'media_url': media_url,
        'cdn_url': settings.CDN_URL,
        'utc_now': datetime.datetime.utcnow(),
        'utc_offset': request.COOKIES.get('utcOffset'),
        'ENVIRONMENT': settings.ENVIRONMENT,
        'SERVER_DOMAIN': settings.DOMAIN_NAME
    }
    
def facebook_settings(request):
    
    
    
    return {
        'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
        'FACEBOOK_APP_URL': settings.FACEBOOK_APP_URL,
        'SIGNED_REQUEST': (request.REQUEST.get('signed_request', None)),
    }
    
def facebook_client_settings(request):
    
    return {
        'FACEBOOK_APPS': settings.FACEBOOK_APPS,
        'SIGNED_REQUEST': (request.REQUEST.get('signed_request', None)),
    }