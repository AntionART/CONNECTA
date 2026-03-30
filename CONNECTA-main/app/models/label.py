"""
Label Model — Tags for Categorizing Conversations.

Labels provide a flexible tagging system for organizing conversations
in the CRM dashboard. Each label has a unique internal name, a
human-readable display_name, and a color for UI rendering.

MVP Integration: Labels are stored in the 'labels' array field of
conversation documents, enabling multi-label filtering and visual
categorization (e.g., 'urgent', 'follow-up', 'vip').
"""

from app.extensions import mongo
from app.models.base import BaseModel
from bson import ObjectId


class Label(BaseModel):
    COLLECTION = 'labels'

    # Data Structure: Simple document with name, display_name, color.
    # 'name' is the machine-readable identifier (e.g., 'urgent'),
    # 'display_name' is the UI label (e.g., 'Urgente'),
    # 'color' is a hex color string for badge rendering.
    @staticmethod
    def create(name, display_name, color='#6B7280'):
        doc = {
            'name': name,
            'display_name': display_name,
            'color': color,
        }
        result = mongo.db[Label.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    @staticmethod
    def find_by_name(name):
        return mongo.db[Label.COLLECTION].find_one({'name': name})

    @staticmethod
    def list_all():
        return list(mongo.db[Label.COLLECTION].find().sort('display_name', 1))



# Business Rule: Label names must be unique.
# The unique index on 'name' prevents duplicate labels from being created.
# MongoDB will raise DuplicateKeyError if a second label with the same
# name is inserted.
def init_label_indexes():
    mongo.db[Label.COLLECTION].create_index('name', unique=True)
