from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime

import logging
from sentry.client.handlers import SentryHandler
logger = logging.getLogger(__name__)

is_logging_setup = False

if not is_logging_setup:
    is_logging_setup = True
    
    try:
        logger.setLevel(settings.LOGGING_LEVEL)
    except:
        logger.setLevel(logging.INFO)
        
    logger.addHandler(SentryHandler())


class FacebookBackend:
    def authenticate(self, fb_user=None):
        
        print('authenticate', fb_user)   
        if not fb_user:
            return None
        
        try:
            user = fb_user.user
            
            if not user:
                user = self.create_user(fb_user)
                
        except User.DoesNotExist:
            user = self.create_user(fb_user)
        
        return user
    
    def create_user(self, fb_user):
        
        logger.info('created new user', extra = {
                'data': { 'fb_user': fb_user}
            })
        
        user = User(username=str(fb_user.uid), password='shitballsbatman') 
        # we want utc, not local
        user.date_joined = datetime.utcnow()
        user.save()
        
        fb_user.user = user
        fb_user.save()
        
        return user
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=str(user_id))
        except User.DoesNotExist:
            return None