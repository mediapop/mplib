# ########################################################
# S3FileField.py
# Extended FileField and ImageField for use with Django and Boto.
#
# Required settings:
#	USE_AMAZON_S3 - Boolean, self explanatory
#	DEFAULT_BUCKET - String, represents the default bucket name to use if one isn't provided
#	AWS_ACCESS_KEY_ID - String
#	AWS_SECRET_ACCESS_KEY - String
#
# ########################################################

from django.db import models
from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.core.files.storage import FileSystemStorage
from django.core.files import File

import os

class S3Storage(FileSystemStorage):
    def __init__(self, bucket_name=None, location=None, base_url=None):
        assert bucket_name
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.bucket_name = bucket_name
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        class S3File(File):
            def __init__(self, key):
                self.key = key
            
            def size(self):
                return self.key.size
            
            def read(self, *args, **kwargs):
                return self.key.read(*args, **kwargs)
            
            def write(self, content):
                self.key.set_contents_from_string(content)
            
            def close(self):
                self.key.close()
                
        return S3File(Key(self.bucket, name))

    def _save(self, name, content):
        # HACK: windows is passing this in backwards which foobars it
        name = name.replace('\\', '/')
        
        key = Key(self.bucket, name)

        if hasattr(content, 'temporary_file_path'):
            key.set_contents_from_filename(content.temporary_file_path())
        elif isinstance(content, File):
            key.set_contents_from_file(content)
        else:
            key.set_contents_from_string(content)
        
        key.set_acl('public-read')
        
        return name

    def delete(self, name):
        self.bucket.delete_key(name)

    def exists(self, name):
        return Key(self.bucket, name).exists()

    def listdir(self, path):
        return [key.name for key in self.bucket.list()]

    def path(self, name):
        raise NotImplementedError

    def size(self, name):
        return self.bucket.get_key(name).size

    def url(self, name):
        return Key(self.bucket, name).generate_url(100000)
    
    def get_available_name(self, name):
        return name
    
    @property
    def bucket(self):
        print ('getting bucket')
        if not hasattr(self, "_s3_bucket"):
            connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY) 
            
            self._s3_bucket = connection.get_bucket(self.bucket_name)
        return self._s3_bucket
    

class S3EnabledFileField(models.FileField):
    def __init__(self, bucket=settings.DEFAULT_BUCKET, verbose_name=None, name=None, upload_to='', storage=None, is_public_read=False, **kwargs):

        storage = S3Storage(bucket)
        super(S3EnabledFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)    
        
        
class S3EnabledImageField(models.ImageField):
    def __init__(self, bucket=settings.DEFAULT_BUCKET, verbose_name=None, name=None, width_field=None, height_field=None, is_public_read=False, **kwargs):

        kwargs['storage'] = S3Storage(bucket)
        super(S3EnabledImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs) 
