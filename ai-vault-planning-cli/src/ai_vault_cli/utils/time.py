from datetime import datetime, timedelta

def get_current_time():
    return datetime.now()

def format_time(dt, format_string="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(format_string)

def get_time_delta(days=0, hours=0, minutes=0):
    return timedelta(days=days, hours=hours, minutes=minutes)

def add_time_to_now(days=0, hours=0, minutes=0):
    return get_current_time() + get_time_delta(days, hours, minutes)

def subtract_time_from_now(days=0, hours=0, minutes=0):
    return get_current_time() - get_time_delta(days, hours, minutes)