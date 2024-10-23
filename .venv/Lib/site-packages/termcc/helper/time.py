
import datetime
import pendulum


def show(dtime, timezone=None):
    if not timezone:
        return int(dtime.strftime("%s"))

    now = dtime.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.timestamp(now)
    now = pendulum.from_timestamp(now)
    return now.in_timezone(timezone)



