"""
Helper utilities for MongoDB document serialization.
"""
from bson import ObjectId
from datetime import datetime, timezone


def serialize_doc(doc):
    """
    Convert a MongoDB document to a JSON-serializable dict.

    Nested Structure: Recursively handles nested dicts within documents.
    List: Iterates over list values, serializing each element.
    Data Structure: Converts ObjectId to string, datetime to ISO format.
    Nested Loop: Dict iteration + list iteration = nested processing.
    """
    if doc is None:
        return None
    result = {}
    # Nested Loop: Dict iteration + list iteration = nested processing
    for key, value in doc.items():
        # Data Structure: Converts ObjectId to string
        if isinstance(value, ObjectId):
            result[key] = str(value)
        # Data Structure: Converts datetime to ISO format
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        # Nested Structure: Recursively handles nested dicts within documents
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        # List: Iterates over list values, serializing each element
        elif isinstance(value, list):
            result[key] = [
                serialize_doc(item) if isinstance(item, dict)
                else str(item) if isinstance(item, ObjectId)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def serialize_docs(docs):
    """
    Convert a list of MongoDB documents.

    List: Maps serialize_doc over an array of documents.
    """
    return [serialize_doc(doc) for doc in docs]
