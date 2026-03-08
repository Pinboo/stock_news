import os
from dotenv import load_dotenv

load_dotenv()

# 钉钉配置
DINGTALK_WEBHOOK = os.getenv('DINGTALK_WEBHOOK', '')
DINGTALK_SECRET = os.getenv('DINGTALK_SECRET', '')  # 可选，使用加签时需要

# 钉钉企业应用配置（可选，使用AppKey/AppSecret方式）
DINGTALK_APPKEY = os.getenv('DINGTALK_APPKEY', '')
DINGTALK_APPSECRET = os.getenv('DINGTALK_APPSECRET', '')
DINGTALK_AGENT_ID = os.getenv('DINGTALK_AGENT_ID', '')
DINGTALK_USER_IDS = os.getenv('DINGTALK_USER_IDS', '')  # 接收人用户ID，逗号分隔

# Tushare配置（可选，提供更稳定的数据源）
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')

# AI模型配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4')

# 股票池
STOCK_POOL = os.getenv('STOCK_POOL', '000001,600519').split(',')

# 推送时间
PUSH_TIME = os.getenv('PUSH_TIME', '09:00,15:30').split(',')
