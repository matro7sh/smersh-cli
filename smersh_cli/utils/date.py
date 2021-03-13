from datetime import datetime, timezone


def date_from_iso(iso):
    return datetime.fromisoformat(iso).astimezone(timezone.utc)


def date_to_iso(date):
    return date.isoformat(timespec='seconds')


def now():
    return datetime.now(timezone.utc)


def format_delta(date1, date2):
    delta = date1 - date2
    seconds = (delta.days * 86400) + delta.seconds

    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        s = f'{days} day' + ('s' if days > 1 else '')
    elif hours > 0:
        s = f'{hours} hour' + ('s' if hours > 1 else '')
    elif minutes > 0:
        s = f'{minutes} minute' + ('s' if minutes > 1 else '')
    else:
        s = f'{seconds} second' + ('s' if seconds > 1 else '')

    return date1 > date2, s
