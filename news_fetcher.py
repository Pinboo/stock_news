import akshare as ak
from datetime import datetime
import time
import random

class NewsFetcher:
    """财经新闻抓取器"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
    
    def _retry_request(self, func, *args, **kwargs):
        """带重试的请求"""
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = self.retry_delay * (attempt + 1) + random.uniform(0, 1)
                    print(f"   等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
                
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"   尝试 {attempt + 1}/{self.max_retries} 失败: {str(e)[:50]}")
                else:
                    raise e
        return None
    
    def get_financial_news(self, limit=10):
        """获取重要财经新闻"""
        try:
            print("   正在获取财经新闻...")
            
            # 使用重试机制获取新闻
            news_df = self._retry_request(ak.stock_news_em, symbol="全部")
            
            if news_df is None or news_df.empty:
                print("   ⚠️  未获取到新闻数据")
                return self._get_fallback_news()
            
            news_list = []
            for idx, row in news_df.head(limit).iterrows():
                news_list.append({
                    'title': row.get('新闻标题', ''),
                    'content': row.get('新闻内容', ''),
                    'time': row.get('发布时间', ''),
                    'source': row.get('文章来源', '')
                })
            
            print(f"   ✓ 获取到 {len(news_list)} 条新闻")
            return news_list
        except Exception as e:
            print(f"   ❌ 获取新闻失败: {str(e)[:100]}")
            return self._get_fallback_news()
    
    def _get_fallback_news(self):
        """获取备用新闻（当主数据源失败时）"""
        print("   ℹ️  使用备用新闻")
        return [
            {
                'title': '数据源暂时不可用',
                'content': '财经新闻数据源连接失败，请稍后重试',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': '系统提示'
            }
        ]
    
    def format_news(self, news_list):
        """格式化新闻为文本"""
        if not news_list:
            return "⚠️  暂无财经新闻（数据源连接失败）"
        
        text = "📰 重要财经新闻\n\n"
        for i, news in enumerate(news_list, 1):
            text += f"{i}. {news['title']}\n"
            text += f"   来源: {news['source']} | {news['time']}\n\n"
        
        return text
