"""
钉钉交互机器人（轮询模式）
无需回调地址，主动轮询群消息
"""
import time
import requests
from datetime import datetime
from stock_data import StockData
from ai_analyzer import AIAnalyzer
from news_fetcher import NewsFetcher
from dingtalk_bot import DingTalkBot
import config
import re

class InteractiveBot:
    """交互式机器人"""
    
    def __init__(self):
        self.stock_data = StockData()
        self.ai_analyzer = AIAnalyzer()
        self.news_fetcher = NewsFetcher()
        self.dingtalk_bot = DingTalkBot()
        self.processed_messages = set()  # 已处理的消息ID
        self.last_check_time = time.time()
    
    def parse_stock_code(self, text):
        """从文本中提取股票代码"""
        # 匹配6位数字的股票代码
        pattern = r'\b\d{6}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def handle_stock_query(self, stock_code):
        """处理股票查询"""
        try:
            print(f"📈 查询股票: {stock_code}")
            
            # 获取股票数据
            stock_info = self.stock_data.get_stock_realtime(stock_code)
            
            if not stock_info:
                return f"❌ 未找到股票代码 {stock_code} 的信息"
            
            # 格式化基本信息
            response = f"📈 {stock_info['name']}({stock_code})\n\n"
            response += f"💰 当前价格: {stock_info['price']:.2f}元\n"
            
            change_emoji = "📈" if stock_info['change'] > 0 else "📉"
            response += f"{change_emoji} 涨跌幅: {stock_info['change']:+.2f}%\n"
            response += f"📊 今开: {stock_info['open']:.2f} | 最高: {stock_info['high']:.2f} | 最低: {stock_info['low']:.2f}\n"
            response += f"💵 成交额: {stock_info['amount']/100000000:.2f}亿\n\n"
            
            # AI分析
            response += "🤖 AI分析:\n"
            analysis = self.ai_analyzer.analyze_stock(stock_info)
            response += analysis
            
            return response
        except Exception as e:
            print(f"❌ 处理股票查询失败: {e}")
            return f"❌ 查询失败，请稍后重试"
    
    def handle_market_query(self):
        """处理大盘查询"""
        try:
            print("📊 查询大盘")
            
            # 获取大盘数据
            market_data = self.stock_data.get_market_index()
            
            if not market_data:
                return "❌ 获取大盘数据失败"
            
            response = "📊 大盘行情\n\n"
            for name, data in market_data.items():
                if data:
                    change_emoji = "📈" if data['change'] > 0 else "📉"
                    response += f"{change_emoji} {name}: {data['price']:.2f} ({data['change']:+.2f}%)\n"
            
            # 获取新闻
            news_list = self.news_fetcher.get_financial_news(limit=3)
            if news_list:
                response += "\n📰 最新财经新闻:\n"
                for i, news in enumerate(news_list[:3], 1):
                    response += f"{i}. {news['title']}\n"
            
            # AI分析
            response += "\n🤖 AI分析:\n"
            analysis = self.ai_analyzer.analyze_market(market_data, news_list)
            response += analysis
            
            return response
        except Exception as e:
            print(f"❌ 处理大盘查询失败: {e}")
            return f"❌ 查询失败，请稍后重试"
    
    def handle_news_query(self):
        """处理新闻查询"""
        try:
            print("📰 查询新闻")
            
            news_list = self.news_fetcher.get_financial_news(limit=5)
            
            if not news_list:
                return "❌ 暂无财经新闻"
            
            response = "📰 最新财经新闻\n\n"
            for i, news in enumerate(news_list, 1):
                response += f"{i}. {news['title']}\n"
                response += f"   来源: {news['source']} | {news['time']}\n\n"
            
            return response
        except Exception as e:
            print(f"❌ 处理新闻查询失败: {e}")
            return f"❌ 查询失败，请稍后重试"
    
    def handle_help(self):
        """处理帮助命令"""
        return """🤖 A股智能分析助手

📋 支持的命令：

1️⃣ 查询个股
   发送: 股票代码
   例如: 000001

2️⃣ 查询大盘
   发送: 大盘 / 指数 / 行情

3️⃣ 查询新闻
   发送: 新闻 / 资讯

4️⃣ 帮助
   发送: 帮助 / help

💡 提示: 直接发送6位股票代码即可查询
⏰ 定时推送: 每天 09:00 和 15:30"""
    
    def process_message(self, text):
        """处理消息并返回回复"""
        text = text.strip()
        text_lower = text.lower()
        
        print(f"\n💬 收到消息: {text}")
        
        # 帮助命令
        if '帮助' in text or 'help' in text_lower:
            return self.handle_help()
        
        # 大盘查询
        if '大盘' in text or '指数' in text or '行情' in text:
            return self.handle_market_query()
        
        # 新闻查询
        if '新闻' in text or '资讯' in text:
            return self.handle_news_query()
        
        # 股票代码查询
        stock_code = self.parse_stock_code(text)
        if stock_code:
            return self.handle_stock_query(stock_code)
        
        # 默认返回帮助
        return "❓ 不理解您的问题，发送「帮助」查看使用说明"
    
    def get_conversation_messages(self):
        """获取会话消息（企业应用模式）"""
        try:
            # 获取access_token
            access_token = self.dingtalk_bot._get_access_token()
            if not access_token:
                return []
            
            # 这里需要根据钉钉的具体API来实现
            # 企业应用可以通过Stream模式接收消息
            # 或者使用群机器人的outgoing机制
            
            # 注意：钉钉企业应用默认不支持主动拉取消息
            # 需要配置Stream模式或Outgoing机制
            
            return []
        except Exception as e:
            print(f"获取消息失败: {e}")
            return []
    
    def run_interactive_mode(self):
        """运行交互模式（命令行测试）"""
        print("\n" + "="*50)
        print("🤖 交互式机器人启动（命令行模式）")
        print("="*50)
        print("\n💡 提示: 在这里输入命令测试机器人功能")
        print("   输入 'quit' 或 'exit' 退出\n")
        
        while True:
            try:
                user_input = input("👤 你: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("\n👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理消息
                response = self.process_message(user_input)
                
                print(f"\n🤖 机器人:\n{response}\n")
                print("-"*50 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")

def main():
    """主函数"""
    bot = InteractiveBot()
    
    print("\n" + "🤖"*25)
    print("A股智能分析交互机器人")
    print("🤖"*25)
    
    print("\n📋 功能说明:")
    print("  - 查询个股: 发送股票代码（如 000001）")
    print("  - 查询大盘: 发送「大盘」或「指数」")
    print("  - 查询新闻: 发送「新闻」或「资讯」")
    print("  - 查看帮助: 发送「帮助」")
    
    print("\n⚠️  当前模式:")
    print("  命令行交互模式 - 用于测试机器人功能")
    print("  在命令行中输入问题，机器人会实时回答")
    
    print("\n💡 提示:")
    print("  钉钉企业应用需要配置Stream模式才能接收群消息")
    print("  或使用群机器人的Outgoing机制")
    print("  详细配置请查看: 交互机器人配置.md")
    
    # 运行交互模式
    bot.run_interactive_mode()

if __name__ == "__main__":
    main()
