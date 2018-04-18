import time

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr as DynamoConditionAttr
from boto3.session import Session as Boto3Session

from django_dynamodb_boss.pool import GetPool


PARTITION_KEY_NAME = getattr(
    settings, 'DYNAMODB_SESSIONS_TABLE_PARTITION_KEY_NAME', 'session_key')
ALWAYS_CONSISTENT = getattr(
    settings, 'DYNAMODB_SESSIONS_ALWAYS_CONSISTENT', True)
TTL = getattr(settings, 'DYNAMODB_SESSIONS_TTL', 60*60*24)


class SessionStore(SessionBase):
    """
    Implements DynamoDB session store.
    """
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self._table = None
        self._dynamodb_boss_pool = GetPool(settings.DYNAMODB_SESSIONS_POOL_NAME)

    def load(self):
        """
        Loads session data from DynamoDB, runs it through the session
        data de-coder (base64->dict), sets ``self.session``.

        :rtype: dict
        :returns: The de-coded session data, as a dict.
        """
        boss = self._dynamodb_boss_pool.Get()
        try:
            table = boss.GetTable(settings.DYNAMODB_SESSIONS_TABLE_NAME)
            response = table.get_item(
                Key={PARTITION_KEY_NAME: self.session_key},
                ConsistentRead=ALWAYS_CONSISTENT)
        finally:
            self._dynamodb_boss_pool.Release(boss)
        if 'Item' in response:
            session_data = response['Item']['data']
            return self.decode(session_data)
        else:
            self.create()
            return {}

    def exists(self, session_key):
        """
        Checks to see if a session currently exists in DynamoDB.

        :rtype: bool
        :returns: ``True`` if a session with the given key exists in the DB,
            ``False`` if not.
        """
        boss = self._dynamodb_boss_pool.Get()
        try:
            table = boss.GetTable(settings.DYNAMODB_SESSIONS_TABLE_NAME)
            response = table.get_item(
                Key={PARTITION_KEY_NAME: session_key},
                ConsistentRead=ALWAYS_CONSISTENT)
        finally:
            self._dynamodb_boss_pool.Release(boss)
        if 'Item' in response:
            return True
        else:
            return False

    def create(self):
        """
        Creates a new entry in DynamoDB. This may or may not actually
        have anything in it.
        """
        while True:
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Saves the current session data to the database.

        :keyword bool must_create: If ``True``, a ``CreateError`` exception
            will be raised if the saving operation doesn't create a *new* entry
            (as opposed to possibly updating an existing entry).
        :raises: ``CreateError`` if ``must_create`` is ``True`` and a session
            with the current session key already exists.
        """
        # If the save method is called with must_create equal to True, I'm
        # setting self._session_key equal to None and when
        # self.get_or_create_session_key is called the new
        # session_key will be created.
        if must_create:
            self._session_key = None
        self._get_or_create_session_key()
        update_kwargs = {
            'Key': {PARTITION_KEY_NAME: self.session_key},
        }
        attribute_names = {'#data': 'data'}
        attribute_values = {
            ':data': self.encode(self._get_session(no_load=must_create))
        }
        set_updates = ['#data = :data']
        if must_create:
            # Set condition to ensure session with same key doesnt exist
            update_kwargs['ConditionExpression'] = \
                DynamoConditionAttr(PARTITION_KEY_NAME).not_exists()
        attribute_values[':expires'] = int(time.time()) + TTL
        set_updates.append('expires = :expires')
        update_kwargs['UpdateExpression'] = 'SET ' + ','.join(set_updates)
        update_kwargs['ExpressionAttributeValues'] = attribute_values
        update_kwargs['ExpressionAttributeNames'] = attribute_names
        try:
            boss = self._dynamodb_boss_pool.Get()
            try:
                table = boss.GetTable(settings.DYNAMODB_SESSIONS_TABLE_NAME)
                table.update_item(**update_kwargs)
            finally:
                self._dynamodb_boss_pool.Release(boss)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                raise CreateError
            raise

    def delete(self, session_key=None):
        """
        Deletes the current session, or the one specified in ``session_key``.

        :keyword str session_key: Optionally, override the session key
            to delete.
        """
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        boss = self._dynamodb_boss_pool.Get()
        try:
            table = boss.GetTable(settings.DYNAMODB_SESSIONS_TABLE_NAME)
            table.delete_item(Key={PARTITION_KEY_NAME: session_key})
        finally:
            self._dynamodb_boss_pool.Release(boss)


