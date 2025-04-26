from .calendar import get_sizhu

def calculate_sizhu(year, month, day, hour=0, minute=0, timezone=None):
    return get_sizhu(year, month, day, hour, minute, timezone)