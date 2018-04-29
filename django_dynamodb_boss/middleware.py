from django_dynamodb_boss.pool import GetBoss, ReleaseBoss


class DynamoDBBossMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        boss = GetBoss()
        try:
            request.dynamodb_boss = boss
            return self.get_response(request)
        finally:
            ReleaseBoss(boss)


