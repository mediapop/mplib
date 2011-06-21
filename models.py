from django.db import models
from django.contrib.auth.models import User

class FacebookUser(models.Model):
    uid = models.BigIntegerField(primary_key=True, unique=True, editable=False)
    
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    flags = models.IntegerField(default=0)    
    
    access_token = models.CharField(max_length=128, editable=False)
    
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    
    time_zone = models.CharField(max_length=8, blank=True)
    gender = models.CharField(max_length=8, blank=True)
    locale = models.CharField(max_length=8, blank=True)  
    email = models.EmailField(max_length=200, blank=True)
    
    user = models.ForeignKey(User, null=True)
    
    def __unicode__(self):
        return '%s, %s' % (self.last_name, self.first_name)
    
    class Meta:
        db_table = u'facebook_user'
    
class FacebookUserIP(models.Model):
    
    fb_user = models.ForeignKey(FacebookUser)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    ip_address = models.IPAddressField(editable=False)
    
    class Meta:
        db_table = u'facebook_user_ip'
    