from django.apps import AppConfig


class DjangoDynamoDBBossConfig(AppConfig):

    name = 'django_dynamodb_boss'

    def ready(self):
        # replace the dynamodb_boss.conf.settings instance with the
        #   django.conf.settings instance
        from django.conf import settings
        from dynamodb_boss import conf
        conf.settings = settings


