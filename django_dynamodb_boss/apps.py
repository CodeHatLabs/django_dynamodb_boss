from django.apps import AppConfig


class DjangoDynamoDBBossConfig(AppConfig):

    name = 'django_dynamodb_boss'

    def ready(self):
        from django.conf import settings
        if not settings.hasattr('DYNAMODB_SESSIONS_POOL_NAME'):
            settings.DYNAMODB_SESSIONS_POOL_NAME = 'default'
        if not settings.hasattr('DYNAMODB_SESSIONS_TABLE_NAME'):
            settings.DYNAMODB_SESSIONS_TABLE_NAME = 'sessions'


