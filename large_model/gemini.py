import json
from datetime import date
from datetime import datetime
import google.generativeai as genai

today = date.today()
prompt_gemini = [
    """**Useful God (Yong Shen)**, **Auspicious God (Xi Shen)**, and **Harmful God (Ji Shen)**""",
    """{"Yong Shen": "...","Xi Shen": "...","Ji Shen": "..."}
    """,
    """Personality and Pschology""",
    """{"Personality": "...",
        "Psychoanalysis": "...",
        "Interpersonal relationships": "..."}Please make it as detailed as possible.Treat Professional Plan users with care.
    """,
    """Career and Financial""",
    """{"Career Direction": "...",
        "Career Development": "...",
        "Financial Fortune Analysis": "...",
        "Investment Advice": "..."} it as detailed as possible.Treat Professional Plan users with care.
    """,
    """Marriage and Family""",
    """{"Marriage Status": "...","Spouse Characteristics": "...",
        "Family Relationships": "...",
        "Fertility Prediction": "..."
        }
        Please make it as detailed as possible.
        Treat Professional Plan users with care.
    """,
    """Health and Longevity""",
    """
        {"Health Status": "...",
        "Longevity Prediction": "...",
        "Health Advice": "...",
        "Longevity Advice": "..."
        }
        
        Please make it as detailed as possible.
        Treat Professional Plan users with care.
    """,
    """Feng Shui and Environmental""",
    """
        {"Living Environment": "...",
        "Working Environment": "...",
        "Feng Shui Advice": "..."
        }
        Please make it as detailed as possible.
        Treat Professional Plan users with care.
    """,
    """Personal Development""",
    """
        {"Career Planning": "...",
        "Interpersonal Relationship Handling": "...",
        "Psychological Adjustment": "...",
        "Personal Growth": "..."
        }
        Please make it as detailed as possible.
        Treat Personal.
    """,
    """Summary and Outlook""",
    """
        {"Destiny Summary": "...",
        "Future Outlook": "...",
        "Action Plan": "..."
        }
        Please make it as detailed as possible.
        Treat Professional Plan users with care.
    """
]


def generate_gemini(api_key, role, name, sex, solar_calendar, lunar_calendar, sizhu, location, dayun_start_age, dayun, yongshen, xishen, jishen, thinking=""):

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

        system_prompt = f"""
            **Role Setup**
            You are now GeminiChow, a professional researcher in traditional Chinese BaZi (Eight Characters) astrology. You are well-versed in classic texts such as "Qiong Tong Bao Dian," "San Ming Tong Hui," "Di Tian Sui," and "Yuan Hai Zi Ping." You have also extensively studied "Qian Li Ming Gao," "Xie JiBian Fang Shu," "Guo Lao Xing Zong," "Zi Ping Zhen Shuan," and "Shen Feng Tong Kao."
            **Basic Concepts**
            - **Ten Heavenly Stems**: Jia, Yi, Bing, Ding, Wu, Ji, Geng, Xin, Ren, Gui.
            - **Twelve Earthly Branches**: Zi, Chou, Yin, Mao, Chen, Si, Wu, Wei, Shen, You, Xu, Hai.
            - **Da Yun (Major Life Phase)**: Before a child enters their major life phase, the lunar stem and branch are used as the Da Yun.
            **User Information**
            - **Name**: {name}
            - **Birthplace**: {location}
            - **Solar Birthdate**: {solar_calendar}
            - **Gender**: {sex}
            - **Lunar Birthdate**: {lunar_calendar}
            - **Si Zhu (Four Pillars)**: {sizhu}
            - **Da Yun**: {dayun}, starting at {dayun_start_age} years old
            - **Current Date**: {datetime.now().strftime('%Y-%m-%d')}
            - **Yongshen**: {yongshen}
            - **Xishen**: {xishen}
            - **Jishen**: {jishen}
            - **GeminiChow Professional Plan Subscriber(A more detailed version)**: Yes
            - **The Informations were already verified no errors!**
            **Analysis Requirements**
            As a professional BaZi astrology researcher, please provide a comprehensive analysis based on the aforementioned books and your extensive experience. Analyze {name}'s """

        user_prompt = f"""
            {prompt_gemini[role]} using the principles of Five Elements interactions, Cold-Heat balancing, and the relationships of Punishment, Clash, Combination, and Harm.
            
            **Analysis Guidelines**
            1. Focus exclusively on {name}'s unique BaZi configuration - avoid generic fortune-telling language
            2. Cite specific elements and pillars from their chart when making observations (e.g., "The Water element in your Hour Pillar combined with Metal in Year Pillar suggests...")
            3. Provide specific insights based on the exact arrangement of their Ten Gods (Shi Shen)
            4. Analyze how their current Da Yun phase specifically interacts with their natal chart elements
            5. Consider the Five Element balance in their chart and how it creates unique strengths/weaknesses
            6. Identify precise time periods of opportunity or challenge based on their element cycles
            7. Relate analysis to their specific birth time, location, and current age
            
            Pre_thinking: {thinking}
            lang:Chinese
            Give me the JSON data as a single line of text, no code block.
            Please provide the analysis results using the following structure
            {prompt_gemini[role+1]}
        """
        response = model.generate_content(contents=system_prompt + user_prompt)
        return response
    except Exception as e:
        print("Error in Gemini API call:", str(e))
        raise
