# A股智能分析系统

## 功能特性
- 自动抓取重要财经新闻
- 获取A股实时行情数据
- AI分析大盘走势和个股
- 每日自动推送到钉钉
- 支持自定义股票池

## 技术栈
- Python 3.8+
- akshare (A股数据)
- requests (API调用)
- schedule (定时任务)
- OpenAI兼容API (支持多种大模型)

## 快速开始

### Windows 用户（推荐）⭐

我们为你准备了一键运行脚本，按顺序双击运行：

1. **0-检查Python.bat** - 检查 Python 是否安装
2. **1-安装依赖.bat** - 自动安装所有依赖
3. **2-测试钉钉.bat** - 测试钉钉机器人配置
4. **3-测试完整功能.bat** - 测试完整分析流程
5. **4-启动定时任务.bat** - 启动定时推送

### 命令行用户

#### 1. 检查 Python
```bash
python --version
```
需要 Python 3.8+。如未安装，访问 https://www.python.org/downloads/

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置系统
打开 `.env` 文件，填写配置。详见：[配置指南.md](配置指南.md)

#### 4. 测试运行
```bash
python test_dingtalk.py    # 测试钉钉
python test_run.py          # 测试完整功能
python main.py              # 启动定时任务
```

### 详细说明
查看 [运行指南.md](运行指南.md) 了解更多

## 配置说明
- `DINGTALK_WEBHOOK`: 钉钉机器人webhook地址
- `OPENAI_API_KEY`: AI模型API密钥
- `OPENAI_BASE_URL`: AI模型API地址
- `MODEL_NAME`: 使用的模型名称
- `STOCK_POOL`: 关注的股票代码列表

## 支持的AI模型
支持所有兼容OpenAI API格式的大模型，包括：
- OpenAI (GPT-4, GPT-3.5)
- 通义千问 (qwen-max, qwen-plus)
- 腾讯混元 (hunyuan-lite, hunyuan-pro)
- 文心一言 (ERNIE-4.0)
- 智谱AI (glm-4)
- DeepSeek (deepseek-chat)
- Moonshot (moonshot-v1)
- 零一万物 (yi-large)
- 本地部署模型 (Ollama, vLLM等)

详细配置请查看 [MODEL_CONFIG.md](MODEL_CONFIG.md)
