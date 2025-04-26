# 天干
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
# 生肖
ZODIACS = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
# 五行
FIVE_ELEMENTS = ["木", "火", "土", "金", "水"]

def get_heavenly_stem(num):
    return HEAVENLY_STEMS[num % 10]

def get_earthly_branch(num):
    return EARTHLY_BRANCHES[num % 12]

def get_zodiac(year):
    return ZODIACS[(year - 4) % 12]

def get_five_elements(stem_index):
    return FIVE_ELEMENTS[stem_index // 2]

def get_cn_year(year):
    cn = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    year_str = str(year)
    result = '二〇'
    for i in range(2, len(year_str)):
        result += cn[int(year_str[i])]
    return result