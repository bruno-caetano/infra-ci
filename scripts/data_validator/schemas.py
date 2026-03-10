"""
Definitions of SQL schemas and row-level validation logic.

Contains functions to validate headers and specific data rows against the schemas.
"""
import data_format as dv
from collections import defaultdict
from datetime import datetime, timezone


def min_datetime_dict():
    return defaultdict(lambda: datetime.max.replace(tzinfo=timezone.utc))

def max_datetime_dict():
    return defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))

def _clone_and_remove(columns, ignore_list):
    if not ignore_list:
        return columns
    ignore_set = set(ignore_list)
    return {k: v for k, v in columns.items() if k not in ignore_set}


# --- Schema Definitions ---
# Structure: 'column_name': {'type': '...', 'required': boolean}

BASE_POSTS_SCHEMA = {
    "post_url": {"type": "text", "required": True},
    "post_original_id": {"type": "text", "required": False},
    "post_description": {"type": "text", "required": False},
    "post_shares_count": {"type": "integer", "required": False},
    "post_comments_count": {"type": "integer", "required": False},
    "post_likes_count": {"type": "integer", "required": False},
    "post_author_username": {"type": "text", "required": True},
    "post_hashtags": {"type": "array", "required": False},
    "post_published_at": {"type": "timestamp", "required": True},
    "post_query": {"type": "text", "required": True},
    "post_validation_status": {"type": "text", "required": True}
}

VALIDATION_STATES = ('VALID','PENDING', 'FLAGGED', 'INVALID')

# Structure: 'old_name': 'new_name'
BASE_POSTS_SUBS = {
    "author_name": "post_author_username",
    "author.uniqueId": "post_author_username",
    "channel_username": "message_channel_name",
    "channel_title": "???",
    "desc": "post_description",
    "likes": "post_likes_count",
    "message_id": "???",
    "post_text": "post_description",
    "text": "post_description",
    "shares": "post_shares_count",
}

PLATFORM_SCHEMAS = {
    # --- X (Twitter) ---
    "x": {
        "post_author_id": {"type": "text", "required": True},
        "post_author_followers_count": {"type": "integer", "required": False},
        "post_author_followings_count": {"type": "integer", "required": False},
        "post_author_tweets_count": {"type": "integer", "required": False},
        "post_author_created_at": {"type": "timestamp", "required": False},
        "post_author_is_verified": {"type": "boolean", "required": False},
        "post_author_user_description": {"type": "text", "required": False},
        "post_location_name": {"type": "text", "required": False},
        "post_type": {"type": "text", "required": False},
        "post_lang": {"type": "text", "required": False},
    },

    # --- Instagram ---
    "instagram": {
        "post_thread_id": {"type": "text", "required": True},
        "post_parent_id": {"type": "text", "required": True},
        "post_author_fullname": {"type": "text", "required": False},
        "post_author_is_verified": {"type": "boolean", "required": True},
        "post_author_avatar_url": {"type": "text", "required": True},
        "post_media_type": {"type": "text", "required": True},
        "post_image_urls": {"type": "array", "required": False},
        "post_location_name": {"type": "text", "required": False},
        "post_location_latitude": {"type": "float", "required": False},
        "post_location_longitude": {"type": "float", "required": False},
    	"post_location_city": {"type": "text", "required": False},
    	"post_source_domain_url": {"type": "text", "required": True}
    },

    # --- YouTube ---
    "youtube": {
        "video_title": {"type": "text", "required": True},
        "video_channel_id": {"type": "text", "required": True},
        "video_views_count": {"type": "integer", "required": False},
    },

    # --- Facebook ---
    "facebook": {
        "post_is_time_estimated": {"type": "boolean", "required": False},
    },

    # --- TikTok ---
    "tiktok": {
        "video_transcription": {"type": "text", "required": False},
        "video_views_count": {"type": "integer", "required": True},
    },

    # --- Telegram ---
    "telegram": {
        "message_chat_id": {"type": "text", "required": False},
        "message_reactions": {"type": "text", "required": False},
        "message_entities": {"type": "text", "required": False},
        "message_has_photo": {"type": "boolean", "required": True},
        "message_has_video": {"type": "boolean", "required": True},
        "message_has_document": {"type": "boolean", "required": True},
        "message_media_group_id": {"type": "text", "required": False},
        "message_edit_date": {"type": "timestamp", "required": False},
        "message_views_count": {"type": "integer", "required": False},
        "message_reply_to": {"type": "text", "required": False},
        "message_shared_from": {"type": "text", "required": False},
        "message_user_id": {"type": "text", "required": False},
        "message_channel_name": {"type": "text", "required": False},
    }
}

def _check_substitutions(actual_headers, subs_dict=BASE_POSTS_SUBS):
    warnings = []
    for old_name in subs_dict:
        new_name = subs_dict[old_name]
        if old_name in actual_headers:
            msg = f'Warning: found "{old_name}" column; did you mean "{new_name}"?'
            warnings.append(msg)
    return warnings

def _check_missing_prefix(prefix, required, found, errors):
    TAM = len(prefix)
    for column in required:
        if column.startswith(prefix) and column[TAM:] in found:
            errors.append(f"Found '{column[TAM:]}' column; did you mean '{column}'?")

def validate_header(actual_headers, platform):
    """
    Validates if the CSV headers contain all required columns for
    both the base 'posts' table and the specific platform table.
    """
    errors = []
    warnings = []

    # check for columns of the 'posts' table
    cols = BASE_POSTS_SCHEMA.keys()
    #print(actual_headers)
    missing_base = [col for col in cols if col not in actual_headers]
    if missing_base:
        errors.append(f"Error: Header missing base columns: {missing_base}")

    _check_missing_prefix('post_', BASE_POSTS_SCHEMA, actual_headers, errors)

    translation_errors = _check_substitutions(actual_headers)
    if translation_errors:
        warnings.extend(translation_errors)
    # check for platform specific columns
    if platform in PLATFORM_SCHEMAS:
        p_schema = PLATFORM_SCHEMAS[platform]
        _check_missing_prefix('post_', p_schema.keys(), actual_headers, errors)
        _check_missing_prefix('message_', p_schema.keys(), actual_headers, errors)
        _check_missing_prefix('video_', p_schema.keys(), actual_headers, errors)
        missing_plat = [col for col in p_schema.keys() if col not in actual_headers]
        if missing_plat:
            warnings.append(f"Header missing {platform} columns: {missing_plat}")
    else:
        errors.append(f"Unknown platform schema: {platform}")
    return errors, warnings

def _validate_single_column(col_name, val, rules):
    """Helper function to validate a single value against its rule."""
    errs = []

    # Handle Empty/Null
    is_empty = val is None or str(val).strip() == ''

    if rules['required'] and is_empty:
        errs.append(f"'{col_name}' is missing or NULL but marked as required.")
    if is_empty:
        return errs # cannot check type, return early

    # URL Check (Convention based)
    if col_name.endswith('url'):
        if not dv.is_valid_url(val):
            errs.append(f"Column '{col_name}' contains invalid URL: '{val}'")
    if col_name.endswith('urls') and len(val) > 2:
        elems = val[1:-1].split(",")
        for e in elems:
            if not dv.is_valid_url(e):
                errs.append(f"Column '{col_name}' contains invalid URL: '{e}'")
    # Type Checks
    t = rules['type']
    valid = True

    warning = ''
    if t == 'uuid': valid = dv.is_valid_uuid(val)
    elif t == 'timestamp': valid = dv.is_valid_iso_timestamp(val)
    elif t == 'integer': valid = dv.is_integer(val)
    elif t == 'float': valid = dv.is_float(val)
    elif t == 'boolean': valid = dv.is_boolean(val)
    # TODO: check JSON validation, it seems to reject valid entries
    #elif t == 'json': valid = dv.is_valid_json(val)
    elif t == 'array': valid, warning = dv.is_postgres_array(val)
    # 'text' accepts any string

    if not valid:
        errs.append(f"Column '{col_name}' expects type '{t}', got invalid value '{val}'")
    if warning:
        errs.append(f"Column '{col_name}': {warning}")
    return errs

def get_timestamp_tags(row, platform):
    tstamps = {}
    #print(row)
    #print(platform)
    for tag in row:
        try:
           if BASE_POSTS_SCHEMA[tag]['type'] == 'timestamp':
               tstamps[tag] = datetime.fromisoformat(str(row[tag]).replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            pass
        try:
           if PLATFORM_SCHEMAS[platform][tag]['type'] == 'timestamp':
               tstamps[tag] = datetime.fromisoformat(str(row[tag]).replace('Z', '+00:00')).replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            pass
    return tstamps



def validate_base_row(row_dict, ignore_list=[]):
    """Validates fields belonging to the 'posts' table."""
    errors = []
    for col, rules in _clone_and_remove(BASE_POSTS_SCHEMA, ignore_list).items():
        # Retrieve value safely (in case of header mismatch, handled elsewhere)
        val = row_dict.get(col)
        errors.extend(_validate_single_column(col, val, rules))
    if 'post_validation_status' not in ignore_list:
        valid_status = row_dict.get('post_validation_status')
        if valid_status is not None and valid_status not in VALIDATION_STATES:
            errors.append(f"'post_validation_status must be one of {VALIDATION_STATES}'")
    return errors

def _validate_instagram_row(row_dict, ignore_list=[]):
    """Instagram specific validation."""
    errors = []
    if "post_location_latitude" not in ignore_list:
        latitude = row_dict.get("post_location_latitude")
        if dv.is_float(latitude) and (float(latitude) < -90 or float(latitude) > 90):
            errors.append(f"Invalid latitude value: {latitude}.")
    if "post_location_longitude" not in ignore_list:
        longitude = row_dict.get("post_location_longitude")
        if dv.is_float(longitude) and (float(longitude) < -180 or float(longitude) > 180):
            errors.append(f"Invalid longitude value: {longitude}.")
    return errors

def validate_platform_row(row_dict, platform, ignore_list):
    """Validates fields belonging to the specific platform table."""
    errors = []
    if platform not in PLATFORM_SCHEMAS:
        return [f"No schema defined for platform '{platform}'"]

    schema = _clone_and_remove(PLATFORM_SCHEMAS[platform], ignore_list)
    for col, rules in schema.items():
        val = row_dict.get(col)
        errors.extend(_validate_single_column(col, val, rules))
    if platform == "instagram":
        errors.extend(_validate_instagram_row(row_dict))
    return errors

def validate_row(row_dict, platform, ignore_list):
    errors = validate_base_row(row_dict, ignore_list)
    errors.extend(validate_platform_row(row_dict, platform, ignore_list))
    tstamps = get_timestamp_tags(row_dict, platform)
    return errors, tstamps

