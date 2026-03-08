import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import quote_plus
import config

class DingTalkBot:
    """
    钉钉机器人（支持两种模式）
    
    模式1: 自定义机器人（Webhook）
    - 使用 DINGTALK_WEBHOOK
    - 可选 DINGTALK_SECRET（加签）
    
    模式2: 企业内部应用（AppKey/AppSecret）
    - 使用 DINGTALK_APPKEY 和 DINGTALK_APPSECRET
    - 支持更多高级功能
    """
    
    def __init__(self):
        # 模式1: Webhook
        self.webhook = config.DINGTALK_WEBHOOK
        self.secret = getattr(config, 'DINGTALK_SECRET', '')
        
        # 模式2: 企业应用
        self.appkey = getattr(config, 'DINGTALK_APPKEY', '')
        self.appsecret = getattr(config, 'DINGTALK_APPSECRET', '')
        self.agent_id = getattr(config, 'DINGTALK_AGENT_ID', '')
        
        # 缓存access_token
        self._access_token = None
        self._token_expire_time = 0
        
        # 判断使用哪种模式
        self.use_app_mode = bool(self.appkey and self.appsecret)
    
    def _get_signed_url(self):
        """生成加签后的URL"""
        if not self.secret:
            return self.webhook
        
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        
        hmac_code = hmac.new(
            secret_enc,
            string_to_sign_enc,
            digestmod=hashlib.sha256
        ).digest()
        
        sign = quote_plus(base64.b64encode(hmac_code))
        
        return f"{self.webhook}&timestamp={timestamp}&sign={sign}"
    
    def _get_access_token(self):
        """获取企业应用access_token"""
        # 检查缓存是否有效
        if self._access_token and time.time() < self._token_expire_time:
            return self._access_token
        
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.appkey,
            "appsecret": self.appsecret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                self._access_token = result['access_token']
                # 提前5分钟过期
                self._token_expire_time = time.time() + result.get('expires_in', 7200) - 300
                return self._access_token
            else:
                print(f"❌ 获取access_token失败: {result}")
                return None
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def _send_work_message(self, content, msg_type="text"):
        """
        通过企业应用发送工作通知
        
        Args:
            content: 消息内容
            msg_type: 消息类型（text/markdown）
        """
        access_token = self._get_access_token()
        if not access_token:
            return False
        
        url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}"
        
        # 构建消息体
        if msg_type == "text":
            msg = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        elif msg_type == "markdown":
            msg = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "A股智能分析",
                    "text": content
                }
            }
        else:
            msg = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": getattr(config, 'DINGTALK_USER_IDS', ''),  # 接收人用户ID列表
            "to_all_user": not getattr(config, 'DINGTALK_USER_IDS', ''),  # 如果没指定用户，发给所有人
            "msg": msg
        }
        
        try:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data),
                timeout=10
            )
            
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 钉钉工作通知发送成功")
                return True
            else:
                print(f"❌ 钉钉工作通知发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 发送钉钉工作通知异常: {e}")
            return False
    
    def send_text(self, content, at_mobiles=None, at_all=False):
        """
        发送文本消息
        
        Args:
            content: 消息内容
            at_mobiles: @的手机号列表，如 ["13800138000"]（仅Webhook模式）
            at_all: 是否@所有人（仅Webhook模式）
        """
        # 企业应用模式
        if self.use_app_mode:
            return self._send_work_message(content, "text")
        
        # Webhook模式
        if not self.webhook:
            print("⚠️  钉钉webhook未配置")
            return False
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        # 添加@功能
        if at_mobiles or at_all:
            data["at"] = {
                "atMobiles": at_mobiles or [],
                "isAtAll": at_all
            }
        
        try:
            url = self._get_signed_url()
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 钉钉消息发送成功")
                return True
            else:
                print(f"❌ 钉钉消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 发送钉钉消息异常: {e}")
            return False
    
    def send_markdown(self, title, content, at_mobiles=None, at_all=False):
        """
        发送Markdown消息
        
        Args:
            title: 消息标题
            content: Markdown格式内容
            at_mobiles: @的手机号列表（仅Webhook模式）
            at_all: 是否@所有人（仅Webhook模式）
        """
        # 企业应用模式
        if self.use_app_mode:
            return self._send_work_message(content, "markdown")
        
        # Webhook模式
        if not self.webhook:
            print("⚠️  钉钉webhook未配置")
            return False
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            }
        }
        
        # 添加@功能
        if at_mobiles or at_all:
            data["at"] = {
                "atMobiles": at_mobiles or [],
                "isAtAll": at_all
            }
        
        try:
            url = self._get_signed_url()
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            
            result = response.json()
            if result.get('errcode') == 0:
                print("✅ 钉钉消息发送成功")
                return True
            else:
                print(f"❌ 钉钉消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 发送钉钉消息异常: {e}")
            return False
