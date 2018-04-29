from django_dynamodb_boss.pool import GetBoss, ReleaseBoss


class DynamoDBBossMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # only create a boss if the request doesn't already have one
        boss = GetBoss() if not hasattr(request, 'dynamodb_boss') else None
        self.dynamodb_boss = getattr(request, 'dynamodb_boss', boss)
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            # only release the boss if we created it
            if boss:
                ReleaseBoss(boss)


