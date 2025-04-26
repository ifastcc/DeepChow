HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def calculate_dayun(month_gan, month_zhi, is_shunxing):
    dayun = []
    current_gan = month_gan
    current_zhi = month_zhi
    for _ in range(8):
        dayun.append(HEAVENLY_STEMS[current_gan] + EARTHLY_BRANCHES[current_zhi])
        if is_shunxing:
            current_gan = (current_gan + 1) % 10
            current_zhi = (current_zhi + 1) % 12
        else:
            current_gan = (current_gan - 1) % 10
            current_zhi = (current_zhi - 1) % 12
    return dayun

# def calculate_dayun(year, month, day, hour, minute, gender):
#     # Import the necessary function to get the year's heavenly stem
#     from sizhu_calculator import get_sizhu
    
#     # Get the SiZhu information to determine the month's heavenly stem and earthly branch
#     sizhu_info = get_sizhu(year, month, day, hour, minute)
    
#     # Extract month's heavenly stem and earthly branch indices
#     month_gan = sizhu_info['sizhu']['month']['stem']['index']
#     month_zhi = sizhu_info['sizhu']['month']['branch']['index']
    
#     # Determine if it's forward or reverse direction based on year's heavenly stem and gender
#     year_gan = sizhu_info['sizhu']['year']['stem']['index']
    
#     # Yang stems (甲丙戊庚壬) are even indices (0,2,4,6,8)
#     # For males with yang stems or females with yin stems, it's forward direction
#     is_male = gender.lower() == "male"
#     is_yang_stem = year_gan % 2 == 0
#     is_shunxing = (is_male and is_yang_stem) or (not is_male and not is_yang_stem)
    
#     # Calculate the 8 DaYun periods
#     dayun = []
#     current_gan = month_gan
#     current_zhi = month_zhi
    
#     for i in range(8):
#         # Calculate the age range for this DaYun period
#         start_age = i * 10
#         end_age = start_age + 9
        
#         # Create the DaYun entry with all required information
#         dayun_entry = {
#             "index": i,
#             "age_range": f"{start_age}-{end_age}",
#             "ganzhi": HEAVENLY_STEMS[current_gan] + EARTHLY_BRANCHES[current_zhi],
#             "heavenly_stem": {
#                 "name": HEAVENLY_STEMS[current_gan],
#                 "index": current_gan
#             },
#             "earthly_branch": {
#                 "name": EARTHLY_BRANCHES[current_zhi],
#                 "index": current_zhi
#             }
#         }
        
#         dayun.append(dayun_entry)
        
#         # Update indices for next DaYun period
#         if is_shunxing:
#             current_gan = (current_gan + 1) % 10
#             current_zhi = (current_zhi + 1) % 12
#         else:
#             current_gan = (current_gan - 1) % 10
#             current_zhi = (current_zhi - 1) % 12
    
#     return dayun