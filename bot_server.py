"""
钉钉机器人交互服务器
支持在群里@机器人问股票信息
"""
from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
import time
import json
from stock_data import StockData
from ai_analyzer import AIAnalyzer
from news_fetcher import NewsFetcher
import config

app = Flask(__name__)
stock_data = StockData()
ai_analyzer = AIAnalyzer()
news_fetcher = NewsFetcher()

def verify_signature(timestamp, sign):
    """验证钉钉签名"""
    if not config.DINGTALK_SECRET:
        return True  # 如果没有配置密钥，跳过验证
    
    secret = config.DINGTALK_SECRET
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    expected_sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign == expected_sign

def parse_stock_code(text):
    """从文本中提取股票代码"""
    import re
    # 匹配6位数字的股票代码
    pattern = r'\b\d{6}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def handle_stock_query(stock_code):
    """处理股票查询"""
    try:
        # 获取股票数据
        stock_info = stock_data.get_stock_realtime(stock_code)
        
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
        analysis = ai_analyzer.analyze_stock(stock_info)
        response += analysis
        
        return response
    except Exception as e:
        print(f"处理股票查询失败: {e}")
        return f"❌ 查询失败: {str(e)}"

def handle_market_query():
    """处理大盘查询"""
    try:
        # 获取大盘数据
        market_data = stock_data.get_market_index()
        
        if not market_data:
            return "❌ 获取大盘数据失败"
        
        response = "📊 大盘行情\n\n"
        for name, data in market_data.items():
            if data:
                change_emoji = "📈" if data['change'] > 0 else "📉"
                response += f"{change_emoji} {name}: {data['price']:.2f} ({data['change']:+.2f}%)\n"
        
        # 获取新闻
        news_list = news_fetcher.get_financial_news(limit=3)
        if news_list:
            response += "\n📰 最新财经新闻:\n"
            for i, news in enumerate(news_list[:3], 1):
                response += f"{i}. {news['title']}\n"
        
        # AI分析
        response += "\n🤖 AI分析:\n"
        analysis = ai_analyzer.analyze_market(market_data, news_list)
        response += analysis
        
        return response
    except Exception as e:
        print(f"处理大盘查询失败: {e}")
        return f"❌ 查询失败: {str(e)}"

def handle_news_query():
    """处理新闻查询"""
    try:
        news_list = news_fetcher.get_financial_news(limit=5)
        
        if not news_list:
            return "❌ 暂无财经新闻"
        
        response = "📰 最新财经新闻\n\n"
        for i, news in enumerate(news_list, 1):
            response += f"{i}. {news['title']}\n"
            response += f"   来源: {news['source']} | {news['time']}\n\n"
        
        return response
    except Exception as e:
        print(f"处理新闻查询失败: {e}")
        return f"❌ 查询失败: {str(e)}"

def handle_help():
    """处理帮助命令"""
    return """🤖 A股智能分析助手

📋 支持的命令：

1️⃣ 查询个股
   @我 + 股票代码
   例如: @我 000001

2️⃣ 查询大盘
   @我 大盘
   @我 指数

3️⃣ 查询新闻
   @我 新闻
   @我 资讯

4️⃣ 帮助
   @我 帮助

💡 提示: 直接发送6位股票代码即可查询"""

def process_message(text):
    """处理消息并返回回复"""
    text = text.strip().lower()
    
    # 帮助命令
    if '帮助' in text or 'help' in text:
        return handle_help()
    
    # 大盘查询
    if '大盘' in text or '指数' in text or '行情' in text:
        return handle_market_query()
    
    # 新闻查询
    if '新闻' in text or '资讯' in text:
        return handle_news_query()
    
    # 股票代码查询
    stock_code = parse_stock_code(text)
    if stock_code:
        return handle_stock_query(stock_code)
    
    # 默认返回帮助
    return handle_help()

@app.route('/webhook', methods=['POST'])
def webhook():
    """处理钉钉机器人回调"""
    try:
        # 获取请求数据
        data = request.json
        
        # 验证签名（如果配置了密钥）
        timestamp = request.headers.get('timestamp', '')
        sign = request.headers.get('sign', '')
        
        if config.DINGTALK_SECRET and not verify_signature(timestamp, sign):
            return jsonify({'errcode': 310000, 'errmsg': 'sign not match'})
        
        # 解析消息
        msg_type = data.get('msgtype')
        
        if msg_type == 'text':
            # 文本消息
            content = data.get('text', {}).get('content', '')
            
            # 处理消息
            response_text = process_message(content)
            
            # 返回回复
            return jsonify({
                'msgtype': 'text',
                'text': {
                    'content': response_text
                }
            })
        
        # 其他类型消息暂不处理
        return jsonify({'errcode': 0, 'errmsg': 'ok'})
        
    except Exception as e:
        print(f"处理webhook失败: {e}")
        return jsonify({'errcode': 500, 'errmsg': str(e)})

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'Bot server is running'})

if __name__ == '__main__':
    print("="*50)
    print("🤖 钉钉机器人交互服务器启动中...")
    print("="*50)
    print("\n📋 支持的功能:")
    print("  - 查询个股: @机器人 + 股票代码")
    print("  - 查询大盘: @机器人 大盘")
    print("  - 查询新闻: @机器人 新闻")
    print("  - 查看帮助: @机器人 帮助")
    print("\n⚠️  注意:")
    print("  1. 需要配置钉钉机器人的回调地址")
    print("  2. 服务器需要有公网IP或使用内网穿透")
    print("  3. 详细配置请查看 交互机器人配置.md")
    print("\n" + "="*50)
    
    # 启动服务器
    app.run(host='0.0.0.0', port=8080, debug=False)
