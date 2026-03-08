# 大模型接入配置指南

本系统支持所有兼容 OpenAI API 格式的大模型。以下是常见模型的配置方式：

## 1. OpenAI（官方）

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

可选模型：`gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`

---

## 2. 通义千问（阿里云）

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max
```

可选模型：
- `qwen-max` - 最强性能
- `qwen-plus` - 性价比高
- `qwen-turbo` - 速度快

获取API Key：https://dashscope.console.aliyun.com/

---

## 3. 文心一言（百度）

```env
OPENAI_API_KEY=your_baidu_api_key
OPENAI_BASE_URL=https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat
MODEL_NAME=ERNIE-4.0-8K
```

可选模型：
- `ERNIE-4.0-8K` - 最新版本
- `ERNIE-3.5-8K` - 经济版

获取API Key：https://console.bce.baidu.com/qianfan/

---

## 4. 智谱AI（ChatGLM）

```env
OPENAI_API_KEY=xxxxxxxxxxxxx.xxxxxxxxxxxxx
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
MODEL_NAME=glm-4
```

可选模型：
- `glm-4` - 最新版本
- `glm-3-turbo` - 快速版本

获取API Key：https://open.bigmodel.cn/

---

## 5. DeepSeek

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

可选模型：`deepseek-chat`, `deepseek-coder`

获取API Key：https://platform.deepseek.com/

---

## 6. Moonshot AI（月之暗面）

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.moonshot.cn/v1
MODEL_NAME=moonshot-v1-8k
```

可选模型：
- `moonshot-v1-8k` - 8K上下文
- `moonshot-v1-32k` - 32K上下文
- `moonshot-v1-128k` - 128K上下文

获取API Key：https://platform.moonshot.cn/

---

## 7. 腾讯混元（Hunyuan）

```env
OPENAI_API_KEY=your_secret_id:your_secret_key
OPENAI_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
MODEL_NAME=hunyuan-lite
```

可选模型：
- `hunyuan-lite` - 轻量版，速度快
- `hunyuan-standard` - 标准版
- `hunyuan-pro` - 专业版，效果最好
- `hunyuan-turbo` - 加速版

获取API Key：https://console.cloud.tencent.com/hunyuan

注意：混元的 API Key 格式为 `SecretId:SecretKey`（用冒号连接）

---

## 8. 零一万物（Yi）

```env
OPENAI_API_KEY=xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.lingyiwanwu.com/v1
MODEL_NAME=yi-large
```

可选模型：`yi-large`, `yi-medium`, `yi-spark`

获取API Key：https://platform.lingyiwanwu.com/

---

## 9. 本地部署模型（Ollama/vLLM等）

如果你使用 Ollama 或 vLLM 本地部署开源模型：

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
MODEL_NAME=qwen2:7b
```

支持的开源模型：
- `llama3:8b`, `llama3:70b`
- `qwen2:7b`, `qwen2:72b`
- `mistral:7b`
- `gemma:7b`

---

## 推荐配置

### 性能优先（准确度高）
- OpenAI GPT-4
- 通义千问 qwen-max
- 智谱 glm-4
- 腾讯混元 hunyuan-pro

### 性价比优先
- DeepSeek deepseek-chat（价格最低）
- 腾讯混元 hunyuan-lite（速度快）
- 通义千问 qwen-turbo
- Moonshot moonshot-v1-8k

### 本地部署（数据安全）
- Ollama + Qwen2:7b
- vLLM + Llama3:8b

---

## 注意事项

1. 不同模型的 API 调用费用不同，请查看各平台定价
2. 国内模型通常响应速度更快
3. 本地部署需要较高的硬件配置（建议至少 16GB 显存）
4. 建议先用小模型测试，确认可用后再切换到大模型
