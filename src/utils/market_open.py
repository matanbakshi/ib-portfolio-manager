from datetime import datetime
import pandas_market_calendars as mcal


def is_market_open(exchange_name):
    exc_cal = mcal.get_calendar(exchange_name)

    today = str(datetime.date(datetime.now()))
    today_schedule = exc_cal.schedule(today, today)

    market_open = today_schedule["market_open"].iloc[0].to_pydatetime()
    market_close = today_schedule["market_close"].iloc[0].to_pydatetime()
    now = datetime.now().astimezone()

    return market_open <= now < market_close
