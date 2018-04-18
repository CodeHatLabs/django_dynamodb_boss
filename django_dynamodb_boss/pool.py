from django.conf import settings

from dynamodb_boss.boss import DynamoDBBossPool


def GetPool(name='default'):
    if not name in GetPool.pool:
        pooldef = settings.DYNAMODB_BOSS_POOLS[name]
        GetPool.pool[name] = DynamoDBBossPool(
            pooldef['AWS_ACCESS_KEY_ID'],
            pooldef['AWS_SECRET_ACCESS_KEY'],
            pooldef['REGION_NAME'],
            pooldef.get('TABLE_NAME_PREFIX', '')
            )
    return GetPool.pool[name]
GetPool.pool = {}


def GetBoss(pool_name=None):
    pool = GetPool(pool_name)
    return pool.Get()


def ReleaseBoss(boss, pool_name=None):
    pool = GetPool(pool_name)
    pool.Release(boss)


