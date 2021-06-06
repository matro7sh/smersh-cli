from datetime import datetime, timezone
import gettext

_ = gettext.gettext


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
        s = f'{days} ' + gettext.ngettext('day', 'days', days)
    elif hours > 0:
        s = f'{hours} ' + gettext.ngettext('hour', 'hours', hours)
    elif minutes > 0:
        s = f'{minutes} ' + gettext.ngettext('minute', 'minutes', minutes)
    else:
        s = f'{seconds} ' + gettext.ngettext('second', 'seconds', seconds)

    return date1 > date2, s
