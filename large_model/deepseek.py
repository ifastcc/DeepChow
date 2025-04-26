import requests
import json
from datetime import date
from datetime import datetime
import logging

today = date.today()

prompt_gemini = [
    """**Useful God (Yong Shen)**, **Auspicious God (Xi Shen)**, and **Harmful God (Ji Shen)**""",
    """
        {"Yong Shen": "分析此命局中的用神特性，详述其在命主八字中的具体表现及如何影响命主一生",
        "Xi Shen": "分析此命局中的喜神特性，详述其如何增强命主的运势，以及在何时何地发挥最大效用",
        "Ji Shen": "分析此命局中的忌神特性，详述其如何制约命主的发展，以及应当如何化解其负面影响"}
    """,
    """Personality and Pschology""",
    """
        {"Personality": "基于命主八字五行强弱和十神关系，分析其性格特点、思维方式和行为模式，指出其性格中的优势和潜在盲点",
        "Psychoanalysis": "从命局组合解析命主的心理特质，包括潜意识倾向、情绪模式和应对压力的方式，分析其心理优势和可能面临的心理挑战",
        "Interpersonal relationships": "详细分析命主在人际关系中的表现模式，包括与家人、朋友、同事的互动特点，以及如何根据八字特性优化人际关系"
        }
    """,
    """Career and Financial""",
    """
        {"Career Direction": "基于命主八字格局和用神特点，分析最适合的职业领域和工作环境，指出哪些行业与命主五行相生相助",
        "Career Development": "分析命主职业发展的关键时期和可能面临的挑战，结合大运流年，指出事业发展的黄金期和需要谨慎的时段",
        "Financial Fortune Analysis": "详细解析命主财运特点，包括财富来源、积累方式和财运波动周期，指出命局中的财星和破财因素",
        "Investment Advice": "根据命主八字特性，提供适合的投资策略和理财方向，指出哪些投资领域与命主五行相符"
        }
    """,
    """Marriage and Family""",
    """
        {"Marriage Status": "分析命主婚姻宫位的强弱和特点，预测婚姻生活的整体质量和可能面临的挑战，指出婚姻中的关键时期",
        "Spouse Characteristics": "基于八字中的夫妻宫和桃花位，描述潜在配偶的性格特点、外貌特征和职业倾向，分析最佳配偶类型",
        "Family Relationships": "解析命主与父母、子女、兄弟姐妹的关系特点，指出家庭关系中的优势和需要注意的方面",
        "Fertility Prediction": "分析子女宫的特点和强弱，预测生育能力和子女数量，以及与子女关系的发展趋势"
        }
    """,
    """Health and Longevity""",
    """
        {"Health Status": "基于命主五行平衡状况，分析体质特点和潜在健康风险，指出命局中的疾厄宫位和对应的身体部位",
        "Longevity Prediction": "分析命主寿元宫的特点，评估长寿潜力和影响寿命的关键因素，指出需要特别注意的时期",
        "Health Advice": "根据命主五行特点，提供针对性的健康建议，包括适合的运动方式、饮食习惯和生活作息",
        "Longevity Advice": "提供延年益寿的具体建议，包括如何调整生活方式、心态和环境以增强命主的寿元"
        }
    """,
    """Feng Shui and Environmental""",
    """
        {"Living Environment": "分析适合命主的居住环境特点，包括方位、布局、颜色和材质，指出哪些环境因素能增强命主的运势",
        "Working Environment": "分析适合命主的工作环境特点，包括办公室位置、座位朝向和环境布置，以提升事业运势",
        "Feng Shui Advice": "根据命主八字五行特点，提供个性化的风水调整建议，包括如何布置家居和工作环境以增强运势"
        }
    """,
    """Personal Development""",
    """
        {"Career Planning": "基于命主八字特点和大运走势，制定阶段性职业发展计划，指出关键发展期和可能的职业转折点",
        "Interpersonal Relationship Handling": "提供根据命主八字特性优化人际关系的具体策略，包括如何处理家庭、职场和社交关系",
        "Psychological Adjustment": "分析命主可能面临的心理挑战，提供针对性的心理调适方法，帮助保持心理平衡",
        "Personal Growth": "基于命局特点，提出个人成长的关键领域和发展方向，指出如何扬长避短，实现个人潜能"
        }
    """,
    """Summary and Outlook""",
    """
        {"Destiny Summary": "综合分析命主八字格局的核心特点和人生主题，总结命局的优势和挑战，指出命运的关键影响因素",
        "Future Outlook": "结合大运流年，预测未来关键时期的发展趋势，指出机遇和挑战，以及如何应对未来变化",
        "Action Plan": "提供具体可行的行动建议，帮助命主扬长避短，趋吉避凶，包括短期和长期的发展策略"
        }
    """
]

def generate_deepseek(api_key, role, name, sex, solar_calendar, lunar_calendar, sizhu, location, dayun_start_age, dayun, yongshen, xishen, jishen, thinking=""):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'Generating DeepSeek analysis for role {role}, user {name}')
    system_message = f"""
        **Role Setup**
        You are now DeepChow, a professional researcher in traditional Chinese BaZi (Eight Characters) astrology. You are well-versed in classic texts such as "Qiong Tong Bao Dian," "San Ming Tong Hui," "Di Tian Sui," and "Yuan Hai Zi Ping." You have also extensively studied "Qian Li Ming Gao," "Xie Ji Bian Fang Shu," "Guo Lao Xing Zong," "Zi Ping Zhen Shuan," and "Shen Feng Tong Kao."

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
        - **DeepChow Professional Plan Subscriber**: Yes
        - **The Informations were already verified no errors!**

        **Analysis Requirements**
        As a professional BaZi astrology researcher, please provide a comprehensive analysis based on the aforementioned books and your extensive experience. Analyze {name}'s 
    """

    user_message = f"""
        {prompt_gemini[role]} using the principles of Five Elements interactions, Cold-Heat balancing, and the relationships of Punishment, Clash, Combination, and Harm.
        
        **Analysis Guidelines**
        1. Focus specifically on {name}'s unique BaZi chart - avoid generic statements that could apply to anyone
        2. Reference specific elements in their chart when making observations (e.g., "Your strong Wood element in Day Pillar indicates...") 
        3. Provide concrete examples of how the chart influences their life rather than vague predictions
        4. Analyze the interactions between specific elements in their chart and how they create unique patterns
        5. Consider the current phase of their Da Yun and how it interacts with their natal chart
        6. Identify specific favorable and unfavorable periods based on their unique element combinations
    
        **Output Format**
        lang:chinese
        Please provide the analysis results using the following JSON structure with no markdown:
        {prompt_gemini[role+1]}
    """

    prompt = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        logger.info('Sending request to DeepSeek API...')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-reasoner",
            "messages": prompt,
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": False
        }
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, data=json.dumps(data))
        response_json = response.json()
        logger.info('Successfully received response from DeepSeek API')

        if 'choices' in response_json and len(response_json['choices']) > 0:
            if 'message' in response_json['choices'][0]:
                if 'reasoning_content' in response_json['choices'][0]['message']:
                    return response_json['choices'][0]['message']['reasoning_content']
                elif 'content' in response_json['choices'][0]['message']:
                    return response_json['choices'][0]['message']['content']

        return response_json
    except Exception as e:
        print(f'Error in DeepSeek API call: {str(e)}')
        generate_deepseek(api_key, role, name, sex, solar_calendar, lunar_calendar, sizhu, location, dayun_start_age, dayun, yongshen, xishen, jishen, thinking="")
        raise

