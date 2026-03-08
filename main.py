import schedule
import time
from datetime import datetime
from stock_data_v2 import StockDataV2
from news_fetcher import NewsFetcher
from ai_analyzer import AIAnalyzer
from dingtalk_bot import DingTalkBot
import config

class StockAnalysisSystem:
    """股票分析系统主程序"""
    
    def __init__(self):
        self.stock_data = StockDataV2()  # 使用V2版本
        self.news_fetcher = NewsFetcher()
        self.ai_analyzer = AIAnalyzer()
        self.dingtalk_bot = DingTalkBot()
    
    def run_analysis(self):
        """执行完整的分析流程"""
        print(f"\n{'='*50}")
        print(f"开始执行分析任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # 1. 获取财经新闻
        print("📰 正在获取财经新闻...")
        news_list = self.news_fetcher.get_financial_news(limit=10)
        news_text = self.news_fetcher.format_news(news_list)
        
        # 2. 获取大盘数据
        print("📊 正在获取大盘数据...")
        market_data = self.stock_data.get_market_index()
        market_text = self.stock_data.format_market_data(market_data)
        
        # 3. AI分析大盘
        print("🤖 AI正在分析大盘...")
        market_analysis = self.ai_analyzer.analyze_market(market_data, news_list)
        
        # 4. 获取并分析个股
        print("📈 正在分析个股...")
        stock_analysis_list = []
        for stock_code in config.STOCK_POOL:
            stock_info = self.stock_data.get_stock_realtime(stock_code)
            if stock_info:
                stock_text = self.stock_data.format_stock_data(stock_info)
                analysis = self.ai_analyzer.analyze_stock(stock_info)
                stock_analysis_list.append(f"{stock_text}   💡 {analysis}\n")
        
        # 5. 组装消息
        message = self._build_message(
            news_text,
            market_text,
            market_analysis,
            stock_analysis_list
        )
        
        # 6. 发送到钉钉
        print("📤 正在发送到钉钉...")
        self.dingtalk_bot.send_text(message)
        
        print(f"\n✅ 分析任务完成\n")
    
    def _build_message(self, news_text, market_text, market_analysis, stock_analysis_list):
        """组装完整消息"""
        message = f"🎯 A股智能分析日报\n"
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        message += f"\n{'-'*40}\n\n"
        
        # 新闻
        message += f"{news_text}\n"
        message += f"{'-'*40}\n\n"
        
        # 大盘
        message += f"{market_text}\n"
        message += f"🤖 AI分析：\n{market_analysis}\n\n"
        message += f"{'-'*40}\n\n"
        
        # 个股
        if stock_analysis_list:
            message += "📈 个股分析\n\n"
            for stock_text in stock_analysis_list:
                message += stock_text
        
        message += f"\n{'-'*40}\n"
        message += "⚠️ 投资有风险，决策需谨慎"
        
        return message
    
    def start_scheduler(self):
        """启动定时任务"""
        print("🚀 股票分析系统启动中...")
        print(f"📅 推送时间: {', '.join(config.PUSH_TIME)}")
        print(f"📊 关注股票: {', '.join(config.STOCK_POOL)}")
        print(f"\n等待定时任务执行...\n")
        
        # 注册定时任务
        for push_time in config.PUSH_TIME:
            schedule.every().day.at(push_time).do(self.run_analysis)
            print(f"✓ 已设置定时任务: 每天 {push_time}")
        
        # 立即执行一次（可选）
        # self.run_analysis()
        
        # 保持运行
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    """主函数"""
    system = StockAnalysisSystem()
    
    # 检查配置
    if not config.DINGTALK_WEBHOOK:
        print("⚠️  警告: 钉钉webhook未配置，请在.env文件中配置DINGTALK_WEBHOOK")
    
    if not config.OPENAI_API_KEY:
        print("⚠️  警告: OpenAI API Key未配置，AI分析功能将不可用")
    
    # 启动定时任务
    system.start_scheduler()

if __name__ == "__main__":
    main()
