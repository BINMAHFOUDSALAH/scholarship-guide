"""Today's date in Saudi Arabia, the clock every deadline on the site is read against.

The live server runs on UTC, three hours behind Riyadh, so plain `date.today()` kept a program closing on
5 Nov "open" until 3 am on 6 Nov in Riyadh. Saudi Arabia has no daylight saving time, so a fixed UTC+3
offset is exact and needs no time-zone package.

`date` here is the standard `datetime.date` with one change: `date.today()` gives the day in Riyadh.
Import it in place of `datetime.date` (tests can still replace `main.date` to fix the day).
"""
from datetime import date as _date, datetime, timedelta, timezone

RIYADH = timezone(timedelta(hours=3), "Asia/Riyadh")


class date(_date):
    @classmethod
    def today(cls):
        now = datetime.now(RIYADH)
        return cls(now.year, now.month, now.day)
