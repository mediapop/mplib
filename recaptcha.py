import urllib2, urllib
from django.conf import settings

import logging
from sentry.client.handlers import SentryHandler

logger = logging.getLogger(__name__)

is_logging_setup = False

if not is_logging_setup:
    is_logging_setup = True
    
    logger.setLevel(settings.LOGGING_LEVEL)
    logger.addHandler(SentryHandler())


API_SSL_SERVER="https://api-secure.recaptcha.net"
API_SERVER="http://api.recaptcha.net"
VERIFY_SERVER="api-verify.recaptcha.net"

RECAPTCHA_PRIVATE_KEY = settings.RECAPTCHA_PRIVATE_KEY
RECAPTCHA_PUBLIC_KEY = settings.RECAPTCHA_PUBLIC_KEY

def verify (challenge,
            reponse,
            remote_ip):
    """
   http://code.google.com/apis/recaptcha/docs/verify.html
   
    URL: http://www.google.com/recaptcha/api/verify
        privatekey (required)    Your private key
        remoteip (required)    The IP address of the user who solved the CAPTCHA.
        challenge (required)    The value of "recaptcha_challenge_field" sent via the form
        response (required)    The value of "recaptcha_response_field" sent via the form

    """

    if not (recaptcha_response_field and recaptcha_challenge_field and
            len (recaptcha_response_field) and len (recaptcha_challenge_field)):
        return {'is_valid': False, 'error_code' : 'incorrect-captcha-sol'}
    

    def encode_if_necessary(s):
        if isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    params = urllib.urlencode ({
            'privatekey': encode_if_necessary(RECAPTCHA_PRIVATE_KEY),
            'remoteip' :  encode_if_necessary(remote_ip),
            'challenge':  encode_if_necessary(challenge),
            'response' :  encode_if_necessary(reponse),
            })

    request = urllib2.Request (
        url = "http://%s/verify" % VERIFY_SERVER,
        data = params,
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
            }
        )
    
    httpresp = urllib2.urlopen (request)

    return_values = httpresp.read ().splitlines ();
    
    httpresp.close();

    return_code = return_values [0]
    
    logger.debug('ReCaptcha Response %s %s', return_values, params)

    if (return_code == "true"):
        return { 'is_valid': True}
    else:
        return  { 'is_valid': False, 'error_code': return_values [1]}