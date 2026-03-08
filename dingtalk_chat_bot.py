"""
钉钉群聊天机器人（Stream模式）
无需云服务器，直接在钉钉群里聊天
"""
import logging
from dingtalk_stream import AckMessage
import dingtalk_stream
from stock_data_v2 import StockDataV2
from ai_analyzer import AIAnalyzer
from news_fetcher import NewsFetcher
import config
import re

# 每个用户保留的最大对话轮数（一问一答算一轮）
MAX_HISTORY_ROUNDS = 10

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ChatBotHandler(dingtalk_stream.ChatbotHandler):
    """聊天机器人处理器"""
    
    def __init__(self):
        super().__init__()
        self.stock_data = StockDataV2()
        self.ai_analyzer = AIAnalyzer()
        self.news_fetcher = NewsFetcher()
        # 对话历史：{user_id: [{"role": ..., "content": ...}, ...]}
        self.conversations = {}
        logging.info("✅ 机器人初始化完成")
    
    def parse_stock_code(self, text):
        """从文本中提取股票代码"""
        pattern = r'\b\d{6}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def _build_context(self, text):
        """根据消息内容实时抓取相关市场数据，作为 AI 的上下文"""
        context_parts = []

        # 识别 6 位数字股票代码
        stock_code = self.parse_stock_code(text)
        if stock_code:
            logging.info(f"📈 获取个股数据: {stock_code}")
            stock_info = self.stock_data.get_stock_realtime(stock_code)
            if stock_info:
                context_parts.append(
                    f"个股实时行情 - {stock_info['name']}({stock_code}):\n"
                    f"  当前价: {stock_info['price']:.2f}元  涨跌幅: {stock_info['change']:+.2f}%\n"
                    f"  今开: {stock_info['open']:.2f}  最高: {stock_info['high']:.2f}  最低: {stock_info['low']:.2f}\n"
                    f"  成交额: {stock_info['amount'] / 1e8:.2f}亿"
                )

        # 识别到大盘/指数关键词时，拉取大盘数据
        if any(k in text for k in ['大盘', '指数', '沪深', '上证', '深证', '创业板', '行情']):
            logging.info("📊 获取大盘数据")
            market_data = self.stock_data.get_market_index()
            if market_data:
                lines = []
                for name, data in market_data.items():
                    if data:
                        lines.append(f"  {name}: {data['price']:.2f} ({data['change']:+.2f}%)")
                context_parts.append("大盘指数:\n" + "\n".join(lines))

        # 识别到新闻/资讯关键词时，拉取新闻
        if any(k in text for k in ['新闻', '资讯', '消息', '热点', '公告']):
            logging.info("📰 获取财经新闻")
            news_list = self.news_fetcher.get_financial_news(limit=5)
            if news_list:
                lines = [f"  {i}. {n['title']}（{n['source']}）" for i, n in enumerate(news_list, 1)]
                context_parts.append("最新财经新闻:\n" + "\n".join(lines))

        return "\n\n".join(context_parts)

    def process_message(self, text, user_id):
        """处理消息：结合对话历史和实时数据，调用 AI 返回回复"""
        text = text.strip()
        logging.info(f"💬 [{user_id}] 收到消息: {text}")

        # 初始化该用户的对话历史
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        history = self.conversations[user_id]

        # 将用户消息加入历史
        history.append({"role": "user", "content": text})

        # 根据消息内容实时拉取数据上下文
        context = self._build_context(text)

        # 调用 AI（带完整对话历史 + 数据上下文）
        response = self.ai_analyzer.chat(history, context)

        # 将 AI 回复加入历史
        history.append({"role": "assistant", "content": response})

        # 超过最大轮数时裁剪（保留最近 N 轮，每轮 = user + assistant 各一条）
        max_messages = MAX_HISTORY_ROUNDS * 2
        if len(history) > max_messages:
            self.conversations[user_id] = history[-max_messages:]

        return response
    
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        """处理钉钉消息"""
        try:
            incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
            text = incoming_message.text.content.strip()
            # 用 sender_staff_id 区分不同用户的对话历史，群聊中也能各自独立
            user_id = getattr(incoming_message, 'sender_staff_id', None) or \
                      getattr(incoming_message, 'sender_id', 'default')

            logging.info(f"📨 收到钉钉消息 [{user_id}]: {text}")

            response_text = self.process_message(text, user_id)
            self.reply_text(response_text, incoming_message)

            logging.info("✅ 回复成功")
            return AckMessage.STATUS_OK, 'OK'

        except Exception as e:
            logging.error(f"❌ 处理消息失败: {e}", exc_info=True)
            return AckMessage.STATUS_SYSTEM_EXCEPTION, str(e)

def main():
    """主函数"""
    print("\n" + "="*50)
    print("🤖 钉钉群聊天机器人启动中...")
    print("="*50)
    
    # 检查配置
    if not config.DINGTALK_APPKEY or not config.DINGTALK_APPSECRET:
        print("\n❌ 错误: 企业应用配置未完成")
        print("\n请在 .env 文件中配置:")
        print("  - DINGTALK_APPKEY")
        print("  - DINGTALK_APPSECRET")
        print("\n详细配置请查看: 钉钉Stream模式配置.md")
        return
    
    print(f"\n✅ AppKey: {config.DINGTALK_APPKEY}")
    print(f"✅ 配置检查通过")
    
    print("\n📋 功能说明:")
    print("  - 在钉钉群里@机器人 + 股票代码")
    print("  - @机器人 + 大盘/新闻/帮助")
    print("  - 机器人会实时回复")
    
    print("\n⚠️  注意:")
    print("  1. 需要在钉钉开发者后台开通Stream模式")
    print("  2. 机器人需要添加到群聊中")
    print("  3. 保持此程序运行")
    
    print("\n" + "="*50)
    print("🚀 正在连接钉钉服务器...")
    print("="*50 + "\n")
    
    try:
        # 创建客户端
        credential = dingtalk_stream.Credential(
            config.DINGTALK_APPKEY,
            config.DINGTALK_APPSECRET
        )
        
        client = dingtalk_stream.DingTalkStreamClient(credential)
        
        # 注册机器人处理器
        client.register_callback_handler(
            dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
            ChatBotHandler()
        )
        
        # 启动客户端
        print("✅ 连接成功！机器人已就绪")
        print("💬 现在可以在钉钉群里@机器人聊天了\n")
        print("按 Ctrl+C 停止\n")
        
        client.start_forever()
        
    except KeyboardInterrupt:
        print("\n\n👋 机器人已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n可能的原因:")
        print("  1. AppKey 或 AppSecret 错误")
        print("  2. 未开通 Stream 模式")
        print("  3. 网络连接问题")
        print("\n详细配置请查看: 钉钉Stream模式配置.md")

if __name__ == "__main__":
    main()
