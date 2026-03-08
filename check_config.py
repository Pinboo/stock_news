"""检查配置是否正确加载"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

print("="*50)
print("配置检查")
print("="*50)

# 检查钉钉配置
print("\n【钉钉配置】")
webhook = os.getenv('DINGTALK_WEBHOOK', '')
appkey = os.getenv('DINGTALK_APPKEY', '')
appsecret = os.getenv('DINGTALK_APPSECRET', '')
agent_id = os.getenv('DINGTALK_AGENT_ID', '')

if webhook:
    print(f"✅ Webhook: {webhook[:50]}...")
else:
    print("❌ Webhook: 未配置")

if appkey:
    print(f"✅ AppKey: {appkey}")
else:
    print("❌ AppKey: 未配置")

if appsecret:
    print(f"✅ AppSecret: {appsecret[:20]}...")
else:
    print("❌ AppSecret: 未配置")

if agent_id:
    print(f"✅ AgentId: {agent_id}")
else:
    print("❌ AgentId: 未配置")

# 检查 AI 配置
print("\n【AI模型配置】")
api_key = os.getenv('OPENAI_API_KEY', '')
base_url = os.getenv('OPENAI_BASE_URL', '')
model_name = os.getenv('MODEL_NAME', '')

if api_key:
    print(f"✅ API Key: {api_key[:20]}...")
else:
    print("❌ API Key: 未配置")

if base_url:
    print(f"✅ Base URL: {base_url}")
else:
    print("❌ Base URL: 未配置")

if model_name:
    print(f"✅ Model: {model_name}")
else:
    print("❌ Model: 未配置")

# 检查股票配置
print("\n【股票配置】")
stock_pool = os.getenv('STOCK_POOL', '')
push_time = os.getenv('PUSH_TIME', '')

if stock_pool:
    print(f"✅ 股票池: {stock_pool}")
else:
    print("❌ 股票池: 未配置")

if push_time:
    print(f"✅ 推送时间: {push_time}")
else:
    print("❌ 推送时间: 未配置")

print("\n" + "="*50)

# 判断配置是否完整
has_dingtalk = bool(webhook or (appkey and appsecret and agent_id))
has_ai = bool(api_key and base_url and model_name)

if has_dingtalk and has_ai:
    print("✅ 配置完整，可以开始测试！")
    print("\n下一步：运行 python test_dingtalk.py")
else:
    print("❌ 配置不完整")
    if not has_dingtalk:
        print("   缺少钉钉配置")
    if not has_ai:
        print("   缺少AI模型配置")
    print("\n请检查 .env 文件")

print("="*50)
