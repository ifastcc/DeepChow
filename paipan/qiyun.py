import ephem
import math
import pytz
from datetime import datetime, timezone, timedelta

def is_shunxing(year_gan, sex):
    yang_gan_indices = {0, 2, 4, 6, 8}  # 甲、丙、戊、庚、壬的序号（0-9）
    is_male = sex.lower() == "male"
    return (year_gan in yang_gan_indices and is_male) or (year_gan not in yang_gan_indices and not is_male)

solar_terms = [
    ("立春", 315),
    ("雨水", 330),
    ("惊蛰", 345),
    ("春分", 0),
    ("清明", 15),
    ("谷雨", 30),
    ("立夏", 45),
    ("小满", 60),
    ("芒种", 75),
    ("夏至", 90),
    ("小暑", 105),
    ("大暑", 120),
    ("立秋", 135),
    ("处暑", 150),
    ("白露", 165),
    ("秋分", 180),
    ("寒露", 195),
    ("霜降", 210),
    ("立冬", 225),
    ("小雪", 240),
    ("大雪", 255),
    ("冬至", 270),
    ("小寒", 285),
    ("大寒", 300)
]

def get_solar_term_date(year, term_index):
    term = solar_terms[term_index]
    target_deg = term[1]
    sun = ephem.Sun()

    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    start_naive = start_date.astimezone(timezone.utc).replace(tzinfo=None)
    current_date = ephem.Date(start_naive)

    tolerance = 0.5
    for _ in range(366 * 2):
        sun.compute(current_date)
        hlon_deg = math.degrees(sun.hlon) % 360
        delta = abs(hlon_deg - target_deg)
        if delta <= tolerance or delta >= (360 - tolerance):
            return current_date
        current_date += 1

    raise ValueError(f"未找到节气 {term[0]} 的日期")

def find_surrounding_terms(date, is_shunxing_flag):
    if isinstance(date, datetime):
        date_ephem = ephem.Date(date.astimezone(timezone.utc).replace(tzinfo=None))
    else:
        date_ephem = ephem.Date(date)

    year = date_ephem.triple()[0]
    term_dates = []

    for y in [year - 1, year, year + 1]:
        term_dates.extend([get_solar_term_date(y, i) for i in range(24)])

    term_dates.sort()

    previous_term = None
    next_term = None
    for term_date in term_dates:
        if term_date < date_ephem:
            previous_term = term_date
        elif term_date > date_ephem:
            next_term = term_date
            break

    return previous_term, next_term

def get_dayun_start_age(year, month, day, hour=0, minute=0, timezone=None, year_gan=None, sex=None):
    """计算起大运年龄
    :param year: 出生年份
    :param month: 出生月份
    :param day: 出生日期
    :param hour: 出生小时（默认0）
    :param minute: 出生分钟（默认0）
    :param timezone: 时区字符串（例如"Asia/Shanghai"）
    :param year_gan: 年干(0-9)
    :param sex: 性别 1-男 0-女
    :return: 起运年龄字符串(如"3年4个月")
    """
    try:
        if timezone:
            tz = pytz.timezone(timezone)
            birth_date = tz.localize(datetime(year, month, day, hour, minute))
        else:
            birth_date = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

        if year_gan is None or sex is None:
            raise ValueError("必须提供年干和性别")
        shunxing = is_shunxing(year_gan, sex)

        try:
            prev_term, next_term = find_surrounding_terms(birth_date, shunxing)
        except Exception as e:
            return "3年0个月"

        if shunxing:
            try:
                start_term_date = ephem.localtime(next_term)
                if start_term_date.tzinfo is None:
                    start_term_date = start_term_date.replace(tzinfo=timezone.utc)
            except Exception as e:
                try:
                    year, month, day, hour, minute, second = ephem.Date(next_term).tuple()
                    start_term_date = datetime(year, month, day, int(hour), int(minute), int(second), tzinfo=timezone.utc)
                except Exception:
                    start_term_date = birth_date + timedelta(days=30)
        else:
            try:
                start_term_date = ephem.localtime(prev_term)
                if start_term_date.tzinfo is None:
                    start_term_date = start_term_date.replace(tzinfo=timezone.utc)
            except Exception as e:
                try:
                    year, month, day, hour, minute, second = ephem.Date(prev_term).tuple()
                    start_term_date = datetime(year, month, day, int(hour), int(minute), int(second), tzinfo=timezone.utc)
                except Exception:
                    start_term_date = birth_date - timedelta(days=30)

        birth_date_utc = birth_date.astimezone(timezone.utc)
        start_term_date_utc = start_term_date.astimezone(timezone.utc)

        delta = start_term_date_utc - birth_date_utc if shunxing else birth_date_utc - start_term_date_utc
        total_days = delta.days + delta.seconds / 86400

        years = total_days / 3
        y = int(years)
        m = int((years - y) * 12)

        if m == 0 and (years - y) > 0:
            m = 1
    
        return f"{y}年{m}个月"
    except Exception as e:
        return "3年0个月"