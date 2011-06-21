COMMON_DB_NAME = 'common'
SENTRY_APP_NAME = 'sentry'

COMMON_DB_APPS = ['sentry', 'geoip', 'helpers']

class SentryRouter(object):
    """A router to control all database operations on models in
    the sentry application"""

    def db_for_read(self, model, **hints):
        "Point all operations on myapp models to 'sentry'"
        if model._meta.app_label == SENTRY_APP_NAME:
            return COMMON_DB_NAME
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on myapp models to 'sentry'"
        if model._meta.app_label == SENTRY_APP_NAME:
            return COMMON_DB_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow relation if both model in sentry is involved"
        if obj1._meta.app_label == SENTRY_APP_NAME and obj2._meta.app_label == SENTRY_APP_NAME:
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the sentry app only appears on the 'sentry' db"
        if db == COMMON_DB_NAME:
            return model._meta.app_label == SENTRY_APP_NAME
        elif model._meta.app_label == SENTRY_APP_NAME:
            return False
        return None
      
class CommonRouter(object):
    """A router to control all database operations on models in
    the common db applications application"""

    def db_for_read(self, model, **hints):
        "Point all operations on myapp models to 'sentry'"
        if model._meta.app_label in COMMON_DB_APPS:
            return COMMON_DB_NAME
        return None

    def db_for_write(self, model, **hints):
        "Point all operations on myapp models to 'sentry'"
        if model._meta.app_label in COMMON_DB_APPS:
            return COMMON_DB_NAME
        return None

    def allow_relation(self, obj1, obj2, **hints):
        "Allow relation if both model in sentry is involved"
        if obj1._meta.app_label in COMMON_DB_APPS and obj2._meta.app_label in COMMON_DB_APPS:
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the sentry app only appears on the 'sentry' db"
        if db == COMMON_DB_NAME:
            return model._meta.app_label in COMMON_DB_APPS
        elif model._meta.app_label in COMMON_DB_APPS:
            return False
        return None
        