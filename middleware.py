from django.conf import settings
from facebook_lib import decode_signed_request

class P3PHeaderMiddleware(object):
    
    def process_response(self, request, response):
        response['P3P'] = getattr(settings, 'P3P_COMPACT', None)
        return response

class IgnoreFbCsrfMiddleware(object):
    def process_request(self, request):
        
        signed_request = request.REQUEST.get('signed_request', None)
        
        signed_request = decode_signed_request(signed_request, settings.FACEBOOK_APP_SECRET)
        
        request.csrf_processing_done = signed_request != None
