import requests
import json

# --- 配置 API 服务地址 ---
# 如果是测试 Render 部署的服务，请替换为你的 Render URL
# 例如: RENDER_API_URL = "https://your-service-name.onrender.com/analyze"
# 如果是测试本地服务，通常是:
# LOCAL_API_URL = "http://127.0.0.1:8000/analyze"

# 选择要测试的 API 地址
# API_ENDPOINT_URL = RENDER_API_URL
API_ENDPOINT_URL = "https://deepchow-7kd0.onrender.com/analyze"  # 默认测试本地
# API_ENDPOINT_URL = "http://127.0.0.1:8000/analyze"  # 默认测试本地

# --- 准备请求数据 ---
# 这些数据需要与你的 API 定义的 AnalyzeRequest 模型匹配
test_payload = {
    "name": "李四",
    "sex": "女",
    "year": 1995,
    "month": 10,
    "day": 15,
    "hour": 14,
    "minute": 30,
    "location": "上海",
    "timezone": "Asia/Shanghai"
}


def call_analyze_api(url, payload):
    """
    调用 /analyze API 端点并打印响应。

    参数:
    url (str): API 端点的完整 URL。
    payload (dict): 要发送的 JSON 请求体。
    """
    try:
        print(f"向 {url} 发送 POST 请求...")
        print(f"请求体: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        # 发送 POST 请求
        # 设置 Content-Type header 为 application/json
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(
            payload), headers=headers, timeout=1800)  # 增加超时时间

        # 检查响应状态码
        if response.status_code == 200:
            print("\n请求成功!")
            try:
                response_data = response.json()
                print("API 响应 (JSON):")
                # print(json.dumps(response_data, indent=2, ensure_ascii=False)) # 打印完整的 JSON

                # 通常我们关心的是 report_markdown
                if "report_markdown" in response_data:
                    print("\n--- 命理分析报告 (Markdown) ---")
                    print(response_data["report_markdown"])
                    print("--- 报告结束 ---")
                else:
                    print("响应中未找到 'report_markdown' 字段。")
                    print("完整响应内容:", response.text)

            except json.JSONDecodeError:
                print("无法解析 JSON 响应。")
                print("原始响应文本:")
                print(response.text)
        else:
            print(f"\n请求失败，状态码: {response.status_code}")
            print("错误响应:")
            try:
                # 尝试以 JSON 格式打印错误，如果失败则打印文本
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"\n请求过程中发生错误: {e}")
    except Exception as e:
        print(f"\n发生未知错误: {e}")


if __name__ == "__main__":
    print("开始测试 API 服务...")
    print("确保你的 FastAPI 服务正在运行。")
    print(f"如果你要测试 Render 服务，请修改 API_ENDPOINT_URL 为你的 Render URL (例如: https://your-service-name.onrender.com/analyze)。")

    # 确保已安装 requests 库: pip install requests
    call_analyze_api(API_ENDPOINT_URL, test_payload)
