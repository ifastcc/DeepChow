import json
from sizhu_calculator import calculate_sizhu
from paipan.dayun import calculate_dayun
from paipan.qiyun import get_dayun_start_age, is_shunxing
from large_model.deepseek import generate_deepseek
from large_model.gemini import generate_gemini
import datetime
import re
import time
import pytz

prompt_gemini = [
    """**Useful God (Yong Shen)**, **Auspicious God (Xi Shen)**, and **Harmful God (Ji Shen)**""",
    """{"Yong Shen": "...","Xi Shen": "...","Ji Shen": "..."}
    """,
    """Personality and Pschology""",
    ["Personality",
        "Psychoanalysis",
        "Interpersonal relationships"
     ],
    """Career and Financial""",
    ["Career Direction",
     "Career Development",
     "Financial Fortune Analysis",
     "Investment Advice"],
    """Marriage and Family""",
    ["Marriage Status",
     "Spouse Characteristics",
     "Family Relationships",
     "Fertility Prediction"
     ],
    """Health and Longevity""",
    ["Health Status",
     "Longevity Prediction",
     "Health Advice",
     "Longevity Advice"
     ],
    """Feng Shui and Environmental""",
    ["Living Environment",
     "Working Environment",
     "Feng Shui Advice"
     ],
    """Personal Development""",
    ["Career Planning",
     "Interpersonal Relationship Handling",
     "Psychological Adjustment",
     "Personal Growth"
     ],
    """Summary and Outlook""",
    ["Destiny Summary",
     "Future Outlook",
     "Action Plan"
     ]
]


def analyze(name, sex, year, month, day, hour, minute, location, timezone, deepseek_api_key, gemini_api_key):
    # current_time = datetime.datetime.now() # No longer needed for filename
    sizhu = calculate_sizhu(year, month, day, hour, minute, timezone)
    shunxing = is_shunxing(sizhu['sizhu']['year']['stem']['index'], sex)
    dayun_start_age = get_dayun_start_age(
        year, month, day, hour, minute, timezone, sizhu['sizhu']['year']['stem']['index'], sex)
    dayun_data = calculate_dayun(
        sizhu['sizhu']['month']['stem']['index'], sizhu['sizhu']['month']['branch']['index'], shunxing)
    # filename = name + '_' + str(current_time).replace(':', '-').replace(' ', '_') + ".md" # Make filename safe
    # file = open(re.sub(r'[\\\\/*?:\"<>|]', '_', filename), "a", encoding='utf-8') # Remove file opening

    report_content = ""  # Initialize an empty string to store report content
    start_total_time = time.time()  # Keep track of total time

    report_content += f"# {name}的命理报告\\n\\n"  # Append to string
    report_content += f"## {name}的命盘\\n"  # Append to string
    report_content += f"""|Year|Month|Day|Hour|
|----|----|----|----|
|{sizhu['sizhu']['year']['stem']['name']}|{sizhu['sizhu']['month']['stem']['name']}|{sizhu['sizhu']['day']['stem']['name']}|{sizhu['sizhu']['hour']['stem']['name']}|
|{sizhu['sizhu']['year']['branch']['name']}|{sizhu['sizhu']['month']['branch']['name']}|{sizhu['sizhu']['day']['branch']['name']}|{sizhu['sizhu']['hour']['branch']['name']}|
"""  # Append to string
    report_content += "\\n"  # Add spacing

    for i in range(1, 8):
        # Capture time at the start of this loop iteration
        loop_start_time = time.time()
        print(f"Starting analysis for section {i}/{7}...")

        # Call DeepSeek API
        print("  Calling DeepSeek API...")
        result_deepseek = generate_deepseek(
            deepseek_api_key,
            2*i,
            name,
            sex,
            sizhu['solar']['datetime'],
            sizhu['lunar']['date'],
            sizhu['sizhu']['full'],
            location,
            dayun_start_age,
            dayun_data,
            "dontknow",  # This part seems fixed, consider if you need dynamic values
            "dontknow",  # This part seems fixed
            "dontknow"  # This part seems fixed
        )
        print("  DeepSeek API call finished.")

        # Call Gemini API
        print("  Calling Gemini API...")
        result_gemini_response = generate_gemini(  # Store the response object
            gemini_api_key,
            2*i,
            name,
            sex,
            sizhu['solar']['datetime'],
            sizhu['lunar']['date'],
            sizhu['sizhu']['full'],
            location,
            dayun_start_age,
            dayun_data,
            "dontknow",  # This part seems fixed
            "dontknow",  # This part seems fixed
            "dontknow",  # This part seems fixed
            result_deepseek
        )

        # Extract text carefully, handling potential errors if response is not as expected
        result_gemini_json = {}  # Initialize with empty dict
        try:
            result_gemini = result_gemini_response.text
            # Attempt to parse the JSON string from Gemini's text response
            result_gemini_json = json.loads(result_gemini)
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error processing Gemini response in iteration {i}: {e}")
            # Handle error - maybe write a placeholder or skip this section
            # Keep result_gemini_json as {}

        print("  Gemini API call finished.")

        # Calculate elapsed time for this iteration
        elapsed_time_this_loop = int(time.time() - loop_start_time)
        print(
            f"Finished section {i}/{7}. Time taken for this iteration: {elapsed_time_this_loop} seconds.")

        # Write results to the string variable
        report_content += f"## {prompt_gemini[2*i]}\\n"  # Append to string
        # Check if the list of sub-sections exists and is a list
        if isinstance(prompt_gemini[2*i+1], list):
            for j in range(len(prompt_gemini[2*i+1])):
                section_title = prompt_gemini[2*i+1][j]
                # Safely access the data from the parsed JSON
                section_content = result_gemini_json.get(
                    # Use .get() for safety
                    section_title, "Analysis not available.")
                # Append to string
                report_content += f"### {section_title}\\n{section_content}\\n\\n"

        # Add a small sleep to be polite to APIs, though not strictly for timing
        time.sleep(1)

    end_total_time = time.time()
    total_elapsed_time = int(end_total_time - start_total_time)
    print(
        f"\\nAnalysis completed successfully for user: {name}. Total time taken: {total_elapsed_time} seconds.")

    # file.close() # Remove file closing

    # Return the assembled Markdown string
    return report_content  # Return the string instead of 0


def do_while_input(prompt, validation_func):
    while True:
        value = input(prompt)
        if validation_func(value):
            return value


if __name__ == '__main__':
    print("================================================================================")
    print("""--------####------------------------------###---#-------------------------------\n
--------#---#----------------------------#---#--#-------------------------------\n
--------#----##--####----####---#####--##-------######---####---#---#---#-------\n
--------#-----#-#----#--#----#--#----#-#--------#----#--#----#--#--#-#--#-------\n
--------#----#--##------#-------#---##--#-------#----#--#----#---#---#-#--------\n
--------####------####---####---####-----#####--#----#---####----##---#---------\n
--------------------------------#-----------------------------------------------\n
--------------------------------#-----------------------------------------------""")
    print("================================================================================")
    print(
        "======================[WuLiang Tianzun Be With You.]============================")
    # Input functions with do-while logic
    name = do_while_input("Your Name:", lambda x: x.strip() != "")

    sex = do_while_input("Your Sex [m/f]:", lambda x: x.lower() in ['m', 'f'])
    sex = 'male' if sex.lower() == 'm' else 'female'

    year = int(do_while_input(
        "Your Birth Year [1900-2100]:", lambda x: x.isdigit() and 1900 <= int(x) <= 2100))

    month = int(do_while_input(
        "Your Birth Month [1-12]:", lambda x: x.isdigit() and 1 <= int(x) <= 12))

    day = int(do_while_input(
        "Your Birth Day [1-31]:", lambda x: x.isdigit() and 1 <= int(x) <= 31))

    hour = int(do_while_input(
        "Your Birth Hour [0-23]:", lambda x: x.isdigit() and 0 <= int(x) <= 23))

    minute = int(do_while_input(
        "Your Birth Minute [0-59]:", lambda x: x.isdigit() and 0 <= int(x) <= 59))

    location = do_while_input(
        "Your Birth Location [e.g., AlbanyCounty,NewYork]:", lambda x: x.strip() != "")

    # Timezone validation using pytz
    available_timezones = set(pytz.all_timezones)
    timezone = do_while_input(f"Your Timezone [e.g., Asia/Shanghai] ({len(available_timezones)} available):",
                              lambda x: x in available_timezones)

    # API keys (replace with real validation if needed)
    deepseek_key = do_while_input(
        "Your DeepSeek API Key:", lambda x: x.strip() != "")
    gemini_key = do_while_input(
        "Your Gemini API Key:", lambda x: x.strip() != "")
    analysis_response = analyze(
        name,
        sex,
        year,
        month,
        day,
        hour,
        minute,
        location,
        timezone,
        deepseek_key,
        gemini_key
    )

    print("\nAnalysis function finished. Report content generated (but not saved to file by default when run directly).")
