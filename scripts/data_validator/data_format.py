"""
Low-level type checking and format validation functions.
"""

import uuid
import json
import re
from datetime import datetime
from urllib.parse import urlparse

def is_valid_uuid(val):
    if not val: return False
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError, AttributeError):
        return False

def is_valid_iso_timestamp(val):
    if not val: return False
    try:
        # Handles ISO 8601. Replaces Z with +00:00 for strict compatibility
        datetime.fromisoformat(str(val).replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def is_valid_url(val):
    if not val: return False
    try:
        result = urlparse(str(val))
        # Checks if scheme (http/https) and netloc (domain) exist
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_integer(val):
    if not val: return False
    try:
        int(val)
        return True
    except (ValueError, TypeError):
        return False

def is_float(val):
    if not val: return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False

def is_boolean(val):
    if not val: return False
    normalized = str(val).strip().lower()
    return normalized in ['true', 'false', '1', '0', 'yes', 'no', 't', 'f']

def is_valid_json(val):
    """Checks if a string is valid JSON (for JSONB columns stored in CSV)."""
    if not val: return False
    try:
        json.loads(str(val))
        return True
    except (ValueError, TypeError):
        return False

def is_postgres_array(val):
    """Checks for Postgres array format: '{item1,item2}'"""
    if not val: return False
    val = str(val).strip()
    has_brackets = False
    warning = ""
    if val.startswith('[') and val.endswith(']'):
        has_brackets = True
    if val.startswith('{') and val.endswith('}'):
        has_brackets = True
    if not has_brackets:
        warning += "Wrong delimiter, arrays should begin/end with '[' ']' or '{' '}'."
    if val.count(";") and not val.count(","):
        warning += " Array separator should be ',' and not ';'."
    return has_brackets, warning

