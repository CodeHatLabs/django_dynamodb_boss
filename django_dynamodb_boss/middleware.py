from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from django_dynamodb_boss.pool import GetPool


class DynamoDBBossMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.dynamodb_boss = SimpleLazyObject(lambda: GetPool())


