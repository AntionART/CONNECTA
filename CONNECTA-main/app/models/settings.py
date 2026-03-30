"""
Settings Model — Key-Value Store for Application Settings.

Provides a flexible key-value configuration store backed by MongoDB.
Used to persist runtime configuration such as WhatsApp API credentials
without requiring environment variable changes or redeployment.

Data Structure: Each document is a simple {key, value} pair.
The unique index on 'key' ensures no duplicate settings.
"""

from app.extensions import mongo


class Settings:
    COLLECTION = 'settings'

    # Dynamic Input: Retrieves a setting by key with optional default.
    # If the key does not exist in the collection, returns the provided
    # default value (None if not specified).
    @staticmethod
    def get(key, default=None):
        doc = mongo.db[Settings.COLLECTION].find_one({'key': key})
        return doc['value'] if doc else default

    # Business Rule: Uses upsert=True — creates if not exists, updates if
    # exists. This makes the set operation idempotent: calling it multiple
    # times with the same key simply overwrites the value without errors.
    @staticmethod
    def set(key, value):
        mongo.db[Settings.COLLECTION].update_one(
            {'key': key},
            {'$set': {'key': key, 'value': value}},
            upsert=True,
        )

    # Nested Structure: Returns a dict aggregating multiple settings keys
    # into a single configuration object for the WhatsApp Evolution API.
    # Professional Output: Provides a clean config dict for WhatsApp service,
    # ready to be consumed by the Evolution API client without further
    # transformation.
    @staticmethod
    def get_evolution_config():
        return {
            'api_url': Settings.get('evolution_api_url', ''),
            'api_key': Settings.get('evolution_api_key', ''),
            'instance_name': Settings.get('evolution_instance_name', ''),
        }

    @staticmethod
    def set_evolution_config(api_url, api_key, instance_name):
        Settings.set('evolution_api_url', api_url)
        Settings.set('evolution_api_key', api_key)
        Settings.set('evolution_instance_name', instance_name)


def init_settings_indexes():
    mongo.db[Settings.COLLECTION].create_index('key', unique=True)
