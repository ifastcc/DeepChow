# DeepChow 周易八卦命理学分析器

## 🔮 项目介绍

欢迎来到 DeepChow 的神秘世界！这是一个基于 DeepSeek 与 Gemini API 的周易八卦命理学分析器，可以说是古老智慧与现代科技的奇妙结合（虽然可能都不太靠谱）。

不过整个逻辑现在还是非常不好，但能跑。

DeepChow 能够根据您的出生年月日时分，从个性、职业、婚姻家庭、健康等多个方面，生成一份看起来非常专业的命理学报告。不管您信不信，它都会非常认真地分析您的八字命盘，仿佛真的能预测您的未来一样！

> ⚠️ 注意：这只是一个个人小玩具，请勿当真，更不要用于重大决策！毕竟，命运掌握在自己手中，而不是 AI 的算法里。

## ✨ 功能特点

- **四柱八字计算**：精确计算您的年、月、日、时四柱八字
- **大运排盘**：分析您的人生大运走势
- **多维度分析**：包括但不限于以下方面（其实就是以下方面）：
  - 个性与心理分析
  - 职业与财运分析
  - 婚姻与家庭分析
  - 健康与寿命预测
  - 风水与环境建议
  - 个人发展规划
  - 命运总结与展望
- **AI 双重分析**：同时调用 DeepSeek 和 Gemini 两大 AI 模型，让您的命理报告更加全面（或者说更加混乱）
- **精美报告生成**：自动生成 Markdown 格式的命理报告，看起来非常专业（尽管内容可能是天马行空）

## 🚀 使用方法

### 前提条件

- Python 3.x
- DeepSeek API 密钥
- Gemini API 密钥
- 一颗愿意尝试新奇事物的心

### 运行程序

```python
from DeepChow.main import analyze

# 调用分析函数
analyze(
    name="张三",  # 您的尊姓大名
    sex="男",  # 性别
    year=1990,  # 出生年
    month=1,  # 出生月
    day=1,  # 出生日
    hour=0,  # 出生时（24小时制）
    minute=0,  # 出生分
    location="北京",  # 出生地点
    timezone="Asia/Shanghai",  # 时区
    deepseek_api_key="your_deepseek_api_key",  # DeepSeek API密钥
    gemini_api_key="your_gemini_api_key"  # Gemini API密钥
)
```

执行后，程序将生成一个以您名字命名的 Markdown 文件，包含详尽的命理分析报告。

## 🧙‍♂️ 项目结构

```
DeepChow/
├── __init__.py
├── main.py                  # 主程序入口
├── large_model/            # AI 模型接口
│   ├── __init__.py
│   ├── deepseek.py         # DeepSeek API 调用
│   └── gemini.py           # Gemini API 调用
├── paipan/                 # 排盘相关
│   ├── __init__.py
│   ├── dayun.py            # 大运计算
│   └── qiyun.py            # 起运年龄计算
└── sizhu_calculator/       # 四柱计算
    ├── __init__.py
    ├── calendar.py         # 日历转换
    └── utils.py            # 工具函数
```

## 🤔 常见问题

**Q: 这个分析准确吗？**  
A: 这个问题问得好！简短回答：不准。长回答：真的不准。

**Q: 为什么要同时使用两个 AI 模型？**  
A: 一个不够玄，两个才够玄！

**Q: 我可以用这个来预测股市吗？**  
A: 理论上可以，实际上......还是别了吧。

## 🛠️ API 服务 (开发中)

为了方便将 DeepChow 的功能集成到其他应用或服务中，我们计划将其封装为一个 API 后端服务。

### 技术选型

- **框架:** FastAPI (提供高性能的异步处理能力和自动交互式文档)

### 接口设计

#### 核心分析接口

- **Endpoint:** `/analyze`
- **Method:** `POST`
- **Request Body (JSON):**
  ```json
  {
    "name": "张三",
    "sex": "男",
    "year": 1990,
    "month": 1,
    "day": 1,
    "hour": 0,
    "minute": 0,
    "location": "北京",
    "timezone": "Asia/Shanghai"
  }
  ```
- **Response Body (JSON):**
  ```json
  {
    "report_markdown": "# 张三 的命理分析报告\n\n## 基本信息\n..." // 包含完整 Markdown 报告的字符串
    // 或者可以考虑返回结构化的 JSON 数据，例如：
    // "report_structured": {
    //   "basic_info": {...},
    "personality_analysis": "...",
    //   ...
    // }
  }
  ```
- **认证:** 暂无。DeepSeek 和 Gemini 的 API Key 将在服务器端配置（例如通过环境变量或配置文件），不由客户端提供。

### 部署与运行

1.  **安装依赖:**

    ```bash
    pip install -r requirements.txt
    # 可能还需要安装 DeepChow 核心逻辑所需的其他依赖
    ```

2.  **配置 API 密钥:**
    在运行服务器之前，设置环境变量：

    ```bash
    export DEEPSEEK_API_KEY="你的DeepSeek密钥"
    export GEMINI_API_KEY="你的Gemini密钥"
    ```

    或者使用其他配置方式（如 `.env` 文件配合 `python-dotenv` 库）。

3.  **启动服务 (在项目根目录):**

    ```bash
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    ```

    - `--reload` 选项可以在代码更改时自动重启服务，方便开发。
    - `--host 0.0.0.0` 使服务可以被局域网内的其他设备访问。
    - `--port 8000` 指定服务监听的端口。

4.  **访问 API 文档:**
    服务启动后，可以在浏览器中访问 `http://127.0.0.1:8000/docs` 查看自动生成的交互式 API 文档并进行测试。

## 📝 免责声明

本项目纯属娱乐，生成的内容完全基于 AI 模型的胡言乱语，不构成任何形式的建议。作者对您基于本工具做出的任何决定不负任何责任。如果您真的相信了这个工具的分析结果，那么......祝您好运！

## 🙏 致谢

感谢 DeepSeek 和 Gemini 提供的 API 服务，让我们能够用最先进的 AI 技术来演绎最古老的哲学。

感谢 DeepSeek 和 Gemini 提供的 API 服务，让我们能够用最先进的 AI 技术来演绎最古老的哲学。

---

> > > > > > > b081e0df8a18615330ecb15706fff1841730d84e
> > > > > > > _DeepChow - 用科技的方式，探索玄学的奥秘（或者说用玄学的方式，消遣科技的无聊）_
