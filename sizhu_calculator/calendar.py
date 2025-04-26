import datetime
from borax.calendars.lunardate import LunarDate
import math
from .utils import *
import pytz

def year_gan_zhi(year):
    year_offset = year - 4
    gan_index = year_offset % 10
    zhi_index = year_offset % 12
    return gan_index, zhi_index

def month_gan_zhi(year_gan, lunar_month):
    month_offset = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}
    zhi_index = (lunar_month + 2 - 1) % 12
    gan_index = (month_offset[year_gan] + lunar_month - 1) % 10
    return gan_index, zhi_index

def day_gan_zhi(solar_date):
    base_date = datetime.date(1900, 1, 31)
    target_date = datetime.date(solar_date.year, solar_date.month, solar_date.day)
    days_diff = (target_date - base_date).days
    gan_index = (0 + days_diff) % 10
    zhi_index = (4 + days_diff) % 12
    return gan_index, zhi_index

def hour_gan_zhi(day_gan, hour):
    time_offset = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
    if hour == 23 or hour < 1:
        zhi_index = 0
    else:
        zhi_index = math.ceil(hour / 2) % 12
    gan_index = (time_offset[day_gan] + zhi_index) % 10
    return gan_index, zhi_index

def solar_to_lunar_and_sizhu(year, month, day, hour=0, minute=0, timezone=None):
    # 处理时区
    if timezone:
        # Handle timezone as integer (offset in hours) or string (timezone name)
        if isinstance(timezone, int):
            # Convert integer timezone offset to UTC offset
            offset = datetime.timedelta(hours=timezone)
            # Create datetime in UTC
            utc_dt = datetime.datetime(year, month, day, hour, minute)
            # Apply offset
            solar_datetime = utc_dt + offset
            solar_date = solar_datetime.date()
            hour = solar_datetime.hour
        else:
            # Handle timezone as string name
            tz = pytz.timezone(timezone)
            solar_datetime = tz.localize(datetime.datetime(year, month, day, hour, minute))
            solar_date = solar_datetime.date()
            hour = solar_datetime.hour
    else:
        solar_date = datetime.date(year, month, day)
  
    lunar_date = LunarDate.from_solar_date(year, month, day)

    # 计算年柱
    year_gan_index, year_zhi_index = year_gan_zhi(lunar_date.year)
    year_stem = get_heavenly_stem(year_gan_index)
    year_branch = get_earthly_branch(year_zhi_index)

    # 计算月柱
    month_gan_index, month_zhi_index = month_gan_zhi(year_gan_index, lunar_date.month)
    month_stem = get_heavenly_stem(month_gan_index)
    month_branch = get_earthly_branch(month_zhi_index)

    # 计算日柱
    day_gan_index, day_zhi_index = day_gan_zhi(solar_date)
    day_stem = get_heavenly_stem(day_gan_index)
    day_branch = get_earthly_branch(day_zhi_index)

    # 计算时柱
    hour_gan_index, hour_zhi_index = hour_gan_zhi(day_gan_index, hour)
    hour_stem = get_heavenly_stem(hour_gan_index)
    hour_branch = get_earthly_branch(hour_zhi_index)

    # 生肖
    zodiac_index = (lunar_date.year - 4) % 12
    zodiac = ZODIACS[zodiac_index]

    # 五行
    year_element_index = year_gan_index // 2
    month_element_index = month_gan_index // 2
    day_element_index = day_gan_index // 2
    hour_element_index = hour_gan_index // 2

    # 农历日期字符串
    lunar_str = f"{get_cn_year(lunar_date.year)}年"
    if lunar_date.leap:
        lunar_str += "闰"
    lunar_str += f"{lunar_date.cn_month}月{lunar_date.cn_day}"

    return {
        "solar": {
            "date": f"{year}年{month}月{day}日",
            "datetime": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"
        },
        "lunar": {
            "year": lunar_date.year,
            "month": lunar_date.month,
            "day": lunar_date.day,
            "is_leap_month": lunar_date.leap,
            "date": lunar_str,
            "zodiac": {"name": zodiac, "index": zodiac_index}
        },
        "sizhu": {
            "year": {
                "stem": {"name": year_stem, "index": year_gan_index},
                "branch": {"name": year_branch, "index": year_zhi_index},
                "element": {"name": FIVE_ELEMENTS[year_element_index], "index": year_element_index}
            },
            "month": {
                "stem": {"name": month_stem, "index": month_gan_index},
                "branch": {"name": month_branch, "index": month_zhi_index},
                "element": {"name": FIVE_ELEMENTS[month_element_index], "index": month_element_index}
            },
            "day": {
                "stem": {"name": day_stem, "index": day_gan_index},
                "branch": {"name": day_branch, "index": day_zhi_index},
                "element": {"name": FIVE_ELEMENTS[day_element_index], "index": day_element_index}
            },
            "hour": {
                "stem": {"name": hour_stem, "index": hour_gan_index},
                "branch": {"name": hour_branch, "index": hour_zhi_index},
                "element": {"name": FIVE_ELEMENTS[hour_element_index], "index": hour_element_index}
            },
            "full": f"{year_stem}{year_branch} {month_stem}{month_branch} {day_stem}{day_branch} {hour_stem}{hour_branch}"
        }
    }

def get_sizhu(year, month, day, hour=0, minute=0, timezone=None):
    return solar_to_lunar_and_sizhu(year, month, day, hour, minute, timezone)

def get_sizhu_json(year, month, day, hour=0, minute=0, timezone=None):
    import json
    result = get_sizhu(year, month, day, hour, minute, timezone)
    return json.dumps(result, ensure_ascii=False, indent=4)