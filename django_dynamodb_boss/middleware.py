from django.utils.deprecation import MiddlewareMixin

from django_dynamodb_boss.pool import GetPool


class DynamoDBBossMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.dynamodb_boss = GetPool().Get()

    def process_response(self, request):
        GetPool().Release(request.dynamodb_boss)


