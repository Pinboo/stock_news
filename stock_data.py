import akshare as ak
import pandas as pd
from datetime import datetime
import time
import random

class StockData:
    """股票数据获取器"""
    
    def __init__(self):
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 2  # 重试延迟（秒）
    
    def _retry_request(self, func, *args, **kwargs):
        """带重试的请求"""
        for attempt in range(self.max_retries):
            try:
                # 添加随机延迟，避免请求过快
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
    
    def get_market_index(self):
        """获取大盘指数数据"""
        result = {}
        try:
            print("   正在获取指数数据...")
            
            # 使用重试机制获取数据
            df = self._retry_request(ak.stock_zh_index_spot_em)
            
            if df is None or df.empty:
                print("   ⚠️  未获取到指数数据")
                return {}
            
            # 查找上证指数
            sh = df[df['名称'].str.contains('上证指数', na=False)]
            if not sh.empty:
                result['上证指数'] = self._parse_index(sh)
                print("   ✓ 上证指数")
            
            # 查找深证成指
            sz = df[df['名称'].str.contains('深证成指', na=False)]
            if not sz.empty:
                result['深证成指'] = self._parse_index(sz)
                print("   ✓ 深证成指")
            
            # 查找创业板指
            cy = df[df['名称'].str.contains('创业板指', na=False)]
            if not cy.empty:
                result['创业板指'] = self._parse_index(cy)
                print("   ✓ 创业板指")
            
            return result
        except Exception as e:
            print(f"   ❌ 获取大盘数据失败: {str(e)[:100]}")
            # 返回模拟数据，避免程序中断
            return self._get_fallback_market_data()
    
    def _get_fallback_market_data(self):
        """获取备用数据（当主数据源失败时）"""
        print("   ℹ️  使用备用数据")
        return {
            '上证指数': {
                'code': '000001',
                'name': '上证指数',
                'price': 3000.0,
                'change': 0.0,
                'volume': 0
            }
        }
    
    def _parse_index(self, df):
        """解析指数数据"""
        if df.empty:
            return None
        
        row = df.iloc[0]
        return {
            'code': row.get('代码', ''),
            'name': row.get('名称', ''),
            'price': row.get('最新价', 0),
            'change': row.get('涨跌幅', 0),
            'volume': row.get('成交量', 0)
        }
    
    def get_stock_realtime(self, stock_code):
        """获取个股实时行情"""
        try:
            print(f"   正在获取 {stock_code}...")
            
            # 使用重试机制获取数据
            df = self._retry_request(ak.stock_zh_a_spot_em)
            
            if df is None or df.empty:
                print(f"   ⚠️  未获取到股票数据")
                return None
            
            stock_data = df[df['代码'] == stock_code]
            
            if stock_data.empty:
                print(f"   ⚠️  未找到股票 {stock_code}")
                return None
            
            row = stock_data.iloc[0]
            print(f"   ✓ {row.get('名称', stock_code)}")
            
            return {
                'code': stock_code,
                'name': row.get('名称', ''),
                'price': row.get('最新价', 0),
                'change': row.get('涨跌幅', 0),
                'volume': row.get('成交量', 0),
                'amount': row.get('成交额', 0),
                'high': row.get('最高', 0),
                'low': row.get('最低', 0),
                'open': row.get('今开', 0)
            }
        except Exception as e:
            print(f"   ❌ 获取股票{stock_code}数据失败: {str(e)[:100]}")
            return None
    
    def format_market_data(self, market_data):
        """格式化大盘数据"""
        if not market_data:
            return "⚠️  暂无大盘数据（数据源连接失败）"
        
        text = "📊 大盘行情\n\n"
        for name, data in market_data.items():
            if data:
                change_emoji = "📈" if data['change'] > 0 else "📉" if data['change'] < 0 else "➡️"
                text += f"{change_emoji} {name}: {data['price']:.2f} "
                text += f"({data['change']:+.2f}%)\n"
        
        return text
    
    def format_stock_data(self, stock_data):
        """格式化个股数据"""
        if not stock_data:
            return ""
        
        change_emoji = "📈" if stock_data['change'] > 0 else "📉" if stock_data['change'] < 0 else "➡️"
        text = f"{change_emoji} {stock_data['name']}({stock_data['code']})\n"
        text += f"   价格: {stock_data['price']:.2f} ({stock_data['change']:+.2f}%)\n"
        text += f"   今开: {stock_data['open']:.2f} | 最高: {stock_data['high']:.2f} | 最低: {stock_data['low']:.2f}\n"
        
        return text
