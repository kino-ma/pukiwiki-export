from datetime import datetime, timezone, timedelta

DEFAULT_TZ = timezone(timedelta(hours=9))


def now_iso():
    dt = datetime.now(tz=DEFAULT_TZ)
    iso = dt.isoformat()
    return iso


def epoch_iso():
    dt = datetime.fromtimestamp(0, tz=DEFAULT_TZ)
    iso = dt.isoformat()
    return iso
