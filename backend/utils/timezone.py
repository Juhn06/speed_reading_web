from datetime import timezone, timedelta
from flask import g, has_request_context, request

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

def _safe_zoneinfo(tz_name):
    if not tz_name:
        return timezone.utc
    if ZoneInfo is None:
        return timezone.utc
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return timezone.utc

def get_request_tz_name():
    if not has_request_context():
        return None
    return request.cookies.get('tz') or request.headers.get('X-Timezone')

def get_request_tz_offset():
    if not has_request_context():
        return None
    offset_value = request.cookies.get('tz_offset') or request.headers.get('X-Timezone-Offset')
    if offset_value is None:
        return None
    try:
        return int(offset_value)
    except ValueError:
        return None

def get_request_timezone():
    if not has_request_context():
        return timezone.utc

    tz_name = get_request_tz_name()
    tzinfo = _safe_zoneinfo(tz_name)
    if tz_name and tzinfo != timezone.utc:
        return tzinfo

    offset_minutes = get_request_tz_offset()
    if offset_minutes is not None:
        return timezone(timedelta(minutes=offset_minutes))

    return timezone.utc

def get_current_timezone():
    if has_request_context() and hasattr(g, 'tz') and g.tz:
        return g.tz
    return get_request_timezone()

def _resolve_timezone(tz_offset=None, tz_name=None):
    if tz_name:
        tzinfo = _safe_zoneinfo(tz_name)
        if tzinfo != timezone.utc:
            return tzinfo
    if tz_offset is not None:
        try:
            return timezone(timedelta(minutes=int(tz_offset)))
        except Exception:
            pass
    return get_current_timezone()

def to_local(dt, tz=None):
    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    tzinfo = tz or get_current_timezone()
    return dt.astimezone(tzinfo)

def format_local_date(dt, tz_offset=None, tz_name=None):
    local = to_local(dt, tz=_resolve_timezone(tz_offset, tz_name))
    return local.strftime('%d/%m/%Y') if local else ''

def format_local_datetime(dt, tz_offset=None, tz_name=None):
    local = to_local(dt, tz=_resolve_timezone(tz_offset, tz_name))
    return local.strftime('%d/%m/%Y %H:%M') if local else ''
