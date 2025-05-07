import json
from datetime import date, datetime
import google.generativeai as genai
from ratelimit import limits, sleep_and_retry, RateLimitException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# from pyrate_limiter import Duration, Rate, Limiter, BucketFullException, BucketIsEmpty # Original
from pyrate_limiter import Duration, Rate, Limiter, BucketFullException  # Corrected
import tiktoken
import time  # For sleeping when TPM limit is hit
import logging

# --- Configuration ---
# RPM (Requests Per Minute) Limiter (using ratelimit)
CALLS_PER_MINUTE = 5
ONE_MINUTE = 60

# RPD (Requests Per Day) Limiter (using ratelimit)
CALLS_PER_DAY = 1000
ONE_DAY_IN_SECONDS = 86400

# TPM (Tokens Per Minute) Limiter (using pyrate-limiter)
TOKENS_PER_MINUTE = 2000000
TOKEN_LIMIT_PERIOD = 60  # seconds
# Estimate for max completion tokens, as Gemini API doesn't take max_tokens for generate_content
# Adjust this based on typical response sizes or model capabilities if known more precisely.
MAX_COMPLETION_TOKENS_ESTIMATE = 2048

# Tenacity Retry Configuration
MAX_RETRIES = 3

# --- Initialize Limiters and Encoders ---
# Tiktoken encoder for TPM
try:
    tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
except Exception as e:
    # Fallback or handle error if tiktoken model is not found, though "cl100k_base" is standard
    logging.error(
        f"Could not load tiktoken encoding: {e}. TPM limiting might not be accurate.")
    tiktoken_encoding = None  # Or a dummy encoder

# Pyrate-limiter for TPM
tpm_rates = [Rate(TOKENS_PER_MINUTE, Duration.SECOND * TOKEN_LIMIT_PERIOD)]
tpm_limiter = Limiter(tpm_rates)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiAPIRateLimitError(Exception):
    "Custom exception for Gemini API 429 errors to be caught by tenacity."
    pass


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


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (GeminiAPIRateLimitError, RateLimitException, genai.types.generation_types.BlockedPromptException)),
    before_sleep=lambda retry_state: logger.info(
        f"Rate limit or API error encountered. Retrying in {retry_state.next_action.sleep:.2f} seconds... (Attempt {retry_state.attempt_number})")
)
@sleep_and_retry  # For RPM and RPD limits from @limits decorator
@limits(calls=CALLS_PER_MINUTE, period=ONE_MINUTE)  # RPM Limit
@limits(calls=CALLS_PER_DAY, period=ONE_DAY_IN_SECONDS)  # RPD Limit
def generate_gemini(api_key, role, name, sex, solar_calendar, lunar_calendar, sizhu, location, dayun_start_age, dayun, yongshen, xishen, jishen, thinking=""):
    # --- Token Counting for TPM ---
    full_prompt_text = (
        # Truncated for brevity, ensure this is the full system prompt
        f'**Role Setup**... (Your extensive system prompt content here, ensure it matches the actual content used) ...'
        # Truncated for brevity
        + f'{prompt_gemini[role]} using the principles of ... (Your extensive user prompt content here, ensure it matches) ...'
    )
    prompt_tokens = 0
    if tiktoken_encoding:
        try:
            prompt_tokens = len(tiktoken_encoding.encode(full_prompt_text))
        except Exception as e:
            logger.warning(
                f"Could not encode prompt to count tokens: {e}. Using 0 prompt tokens for TPM.")

    total_tokens_estimate = prompt_tokens + MAX_COMPLETION_TOKENS_ESTIMATE
    # More specific item ID if needed, or global
    item_id_for_tpm = f"gemini_tpm_{name}_{role}"

    # --- TPM Limiting Loop (pyrate-limiter) ---
    acquired_token_permit = False
    while not acquired_token_permit:
        try:
            tpm_limiter.try_acquire(
                item_id_for_tpm, weight=total_tokens_estimate)
            acquired_token_permit = True
            logger.debug(
                f"TPM: Acquired {total_tokens_estimate} tokens for {item_id_for_tpm}")
        except BucketFullException as e:
            sleep_duration = e.meta_info.get('remaining_time', TOKEN_LIMIT_PERIOD /
                                             TOKENS_PER_MINUTE * total_tokens_estimate + 1)  # Estimate if not available
            # Ensure sleep_duration is at least a small positive number
            sleep_duration = max(0.1, sleep_duration)
            logger.info(
                f"TPM limit hit for {item_id_for_tpm} (requested {total_tokens_estimate} tokens). Waiting for {sleep_duration:.2f} seconds.")
            time.sleep(sleep_duration)
        # except BucketIsEmpty: # This should ideally not be hit often with try_acquire if logic is correct
        #     logger.warning(f"TPM bucket unexpectedly empty for {item_id_for_tpm}. Waiting...")
        #     time.sleep(1) # Default short wait

    # --- Actual API Call ---
    try:
        logger.debug(
            f"Attempting to call Gemini API for {name}, role {role} after passing all rate limiters")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Reconstruct the actual prompts to be sent
        system_prompt_actual = f"""
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

        user_prompt_actual = f"""
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

        response = model.generate_content(
            contents=system_prompt_actual + user_prompt_actual)
        logger.debug(f"Successfully called Gemini API for {name}, role {role}")
        return response
    except genai.types.generation_types.BlockedPromptException as e:
        logger.error(
            f"Gemini API blocked the prompt for {name}, role {role}. Reason: {e}")
        raise
    except Exception as e:
        if "429" in str(e) or isinstance(e, genai.types.generation_types.StopCandidateException):
            logger.warning(
                f"Gemini API rate limit likely hit or other API issue for {name}, role {role}: {str(e)}")
            raise GeminiAPIRateLimitError(f"Gemini API Error: {str(e)}")
        else:
            logger.error(
                f"Unexpected error in Gemini API call for {name}, role {role}: {str(e)}")
            raise
