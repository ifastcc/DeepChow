import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys

# 将项目根目录添加到 sys.path，以便能够导入 DeepChow 模块
# 注意：这依赖于 API 服务从项目根目录启动
# 或者需要更健壮的路径处理方式
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入原始的分析函数
# 假设原始的 main.py 结构允许这样导入
# 可能需要调整 DeepChow/main.py 的结构或导入方式
try:
    from main import analyze as deepchow_analyze
except ImportError as e:
    print(f"Error importing deepchow_analyze: {e}")
    # 在无法导入时提供一个假的函数，以便 API 仍能启动，但会报错

    async def deepchow_analyze(*args, **kwargs):
        raise RuntimeError(
            "Failed to import deepchow_analyze. Check project structure and main.py.")

# --- FastAPI 应用 ---
app = FastAPI(
    title="DeepChow API",
    description="API for the DeepChow 周易八卦命理学分析器",
    version="0.1.0"
)

# --- API 请求模型 ---


class AnalyzeRequest(BaseModel):
    name: str
    sex: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location: str
    timezone: str = "Asia/Shanghai"  # 提供默认值

# --- API 响应模型 ---


class AnalyzeResponse(BaseModel):
    report_markdown: str


# --- API 密钥配置 (临时硬编码 - 需要改进) ---
# !! 重要提示: !!
# 在生产环境中，绝不应将 API 密钥硬编码在代码中。
# 应使用环境变量、配置文件或密钥管理服务。
# 从环境变量读取，如果未设置则使用占位符
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "YOUR_DEEPSEEK_API_KEY_HERE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

if DEEPSEEK_API_KEY == "YOUR_DEEPSEEK_API_KEY_HERE" or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("\n*** 警告: DeepSeek 或 Gemini API 密钥未配置。请设置 DEEPSEEK_API_KEY 和 GEMINI_API_KEY 环境变量。 API 可能无法正常工作。 ***\n")


# --- API 端点 ---
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(request: AnalyzeRequest):
    """
    接收用户基本信息，调用 DeepChow 分析核心逻辑，返回命理分析报告 (Markdown 格式)。
    """
    print(
        f"[API LOG /analyze] Received request for user: {request.name}, Sex: {request.sex}, DOB: {request.year}-{request.month}-{request.day}")

    # 检查 API 密钥是否已配置 (这部分逻辑已存在，但强调其重要性)
    if DEEPSEEK_API_KEY == "YOUR_DEEPSEEK_API_KEY_HERE" or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("[API LOG /analyze] CRITICAL ERROR: DeepSeek or Gemini API key is not configured in environment variables!")
        # 考虑是否应该提前抛出错误，而不是继续执行
        # raise HTTPException(status_code=500, detail="Server configuration error: API keys not set.")

    try:
        print(
            f"[API LOG /analyze] Preparing to call core analysis function (deepchow_analyze) for: {request.name}")
        # 调用核心分析函数
        # 注意：原始 analyze 函数可能不是异步的，FastAPI 会在线程池中运行它
        report_content = deepchow_analyze(
            name=request.name,
            sex=request.sex,
            year=request.year,
            month=request.month,
            day=request.day,
            hour=request.hour,
            minute=request.minute,
            location=request.location,
            timezone=request.timezone,
            deepseek_api_key=DEEPSEEK_API_KEY,
            gemini_api_key=GEMINI_API_KEY
        )
        print(
            f"[API LOG /analyze] Core analysis function (deepchow_analyze) completed for: {request.name}")

        # 确认 analyze 函数返回的是字符串
        if not isinstance(report_content, str):
            print(
                f"[API LOG /analyze] ERROR: Core analysis function (deepchow_analyze) did not return a string. Returned type: {type(report_content)} for user: {request.name}")
            raise HTTPException(
                status_code=500, detail="Internal server error: Analysis function returned unexpected data type.")

        print(
            f"[API LOG /analyze] Analysis complete, preparing response for: {request.name}. Report length: {len(report_content)} characters.")
        return AnalyzeResponse(report_markdown=report_content)

    except RuntimeError as e:
        # 特别处理导入失败的情况
        if "Failed to import deepchow_analyze" in str(e):
            print(
                f"[API LOG /analyze] CRITICAL ERROR: Failed to import core analysis module (deepchow_analyze). Error: {e}")
            raise HTTPException(
                status_code=500, detail="Internal server error: Core analysis module not loaded.")
        else:
            print(
                f"[API LOG /analyze] RUNTIME ERROR during analysis for {request.name}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error during analysis: {e}")
    except HTTPException as http_e:  # 重新抛出已知的 HTTPException
        print(
            f"[API LOG /analyze] HTTP EXCEPTION during processing for {request.name}: {http_e.detail}")
        raise http_e
    except Exception as e:
        print(
            f"[API LOG /analyze] UNEXPECTED ERROR processing request for {request.name}: {e}")
        # 避免泄露过多内部细节给客户端
        raise HTTPException(
            status_code=500, detail="Internal server error processing the request.")

# --- 用于本地测试运行 ---
if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server for local testing...")
    print("Access the API documentation at http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
