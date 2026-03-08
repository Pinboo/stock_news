# 使用指南

本项目是一个 A 股智能分析机器人，自动抓取股票行情、财经新闻，通过 AI 生成分析报告，定时推送到钉钉群，也支持在钉钉群内@机器人实时问答。

## 功能一览

| 功能 | 说明 |
|------|------|
| 定时推送 | 每天开盘/收盘后自动推送大盘 + 个股 + 新闻 + AI 分析 |
| 聊天机器人 | 在钉钉群@机器人，实时查询股票、大盘、新闻 |
| 多数据源 | 支持 akshare / tushare / yfinance / baostock，自动切换 |
| 多 AI 模型 | 支持 OpenAI、通义千问、DeepSeek、文心一言等兼容接口 |
| 自定义股票池 | 在 `.env` 中配置关注的股票代码 |

---

## 环境要求

- Python 3.8+
- 钉钉机器人（Webhook 或企业应用）
- 任意兼容 OpenAI 格式的 AI 模型 API Key

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Pinboo/stock_news.git
cd stock_news
```

### 2. 安装依赖

```bash
# 建议使用虚拟环境
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. 配置 `.env`

项目根目录已提供 `.env` 模板，直接编辑填入真实值：

```bash
# Linux / macOS
nano .env

# Windows 用记事本打开
notepad .env
```

**必填项：**

```env
# 钉钉 Webhook（方式一，简单推荐）
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=你的token

# AI 模型
OPENAI_API_KEY=你的api_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

完整配置说明见 [配置说明](#配置说明) 章节。

### 4. 测试配置

```bash
python check_config.py    # 检查配置是否正确
python test_dingtalk.py   # 测试钉钉推送
python test_run.py        # 立即执行一次完整分析
```

### 5. 启动服务

```bash
# 定时推送（每天 09:00 和 15:30 自动推送）
python main.py

# 聊天机器人（需配置钉钉企业应用 Stream 模式）
python dingtalk_chat_bot.py
```

---

## 配置说明

### 钉钉配置（二选一）

**方式一：自定义机器人 Webhook（简单，只支持推送）**

1. 钉钉群 → 智能群助手 → 添加机器人 → 自定义
2. 复制 Webhook 地址填入 `DINGTALK_WEBHOOK`
3. 如果开启了加签，将密钥填入 `DINGTALK_SECRET`

**方式二：企业内部应用（支持聊天机器人双向交互）**

1. 进入[钉钉开发者后台](https://open-dev.dingtalk.com/)
2. 应用开发 → 企业内部开发 → 创建应用
3. 开通"机器人"能力，开启 Stream 模式
4. 将 AppKey / AppSecret / AgentId 填入对应配置项
5. 详见项目内 `DINGTALK_SETUP.md`

### AI 模型配置

支持所有兼容 OpenAI 接口的模型：

| 模型 | BASE_URL | MODEL_NAME |
|------|----------|------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-max` |
| 腾讯混元 | `https://api.hunyuan.cloud.tencent.com/v1` | `hunyuan-pro` |
| 文心一言 | `https://qianfan.baidubce.com/v2` | `ERNIE-4.0-8K` |
| 智谱 AI | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |
| Moonshot | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |

### 股票与推送时间

```env
# 股票池（逗号分隔的 A 股代码）
STOCK_POOL=000001,600519,000858,601318

# 推送时间（24 小时制，逗号分隔）
PUSH_TIME=09:00,15:30
```

### 数据源配置（可选）

如需使用 Tushare 获取更稳定的数据：

1. 注册 [Tushare](https://tushare.pro/) 并获取 Token
2. 填入 `TUSHARE_TOKEN`

---

## 云服务器部署

### 使用 systemd 守护进程（Linux 推荐）

**1. 上传代码到服务器**

```bash
git clone https://github.com/Pinboo/stock_news.git /home/ubuntu/stock_news
cd /home/ubuntu/stock_news
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. 设置时区**

```bash
sudo timedatectl set-timezone Asia/Shanghai
```

**3. 创建 systemd 服务**

```bash
sudo nano /etc/systemd/system/stock-bot.service
```

写入以下内容（替换用户名和路径）：

```ini
[Unit]
Description=Stock Analysis Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stock_news
ExecStart=/home/ubuntu/stock_news/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. 启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-bot
sudo systemctl start stock-bot

# 查看运行状态
sudo systemctl status stock-bot

# 查看日志
sudo journalctl -u stock-bot -f
```

---

## 聊天机器人使用方法

在钉钉群@机器人发送以下指令：

```
@机器人 000001        # 查询平安银行
@机器人 600519        # 查询贵州茅台
@机器人 大盘          # 查询今日大盘行情
@机器人 新闻          # 查询最新财经新闻
@机器人 帮助          # 查看帮助
```

> 聊天机器人需要配置企业内部应用（方式二），并开启 Stream 模式。

---

## 文件说明

```
├── main.py                 # 定时推送主程序
├── dingtalk_chat_bot.py    # 聊天机器人主程序
├── stock_data_v2.py        # 股票数据获取（多数据源）
├── ai_analyzer.py          # AI 分析模块
├── news_fetcher.py         # 财经新闻抓取
├── dingtalk_bot.py         # 钉钉推送封装
├── config.py               # 配置加载
├── check_config.py         # 配置检查工具
├── .env                    # 配置文件（填写你的密钥）
├── requirements.txt        # 依赖列表
└── DINGTALK_SETUP.md       # 钉钉详细配置指南
```

---

## 常见问题

**Q：推送时间不对？**
服务器时区需设置为 `Asia/Shanghai`，执行 `timedatectl set-timezone Asia/Shanghai`。

**Q：数据获取失败？**
akshare 需要能访问国内网络，海外服务器可能受限，建议使用国内云服务器（阿里云/腾讯云）。

**Q：OpenAI 接口无法访问？**
国内服务器需使用代理或替换为国内大模型（DeepSeek / 通义千问等），修改 `OPENAI_BASE_URL` 和 `MODEL_NAME` 即可。

**Q：聊天机器人不回复？**
检查是否开通了 Stream 模式，并确认 `DINGTALK_APPKEY` / `DINGTALK_APPSECRET` 配置正确。

---

## License

MIT
