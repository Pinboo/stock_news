from openai import OpenAI
import config

class AIAnalyzer:
    """AI分析器"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
    
    def analyze_market(self, market_data, news_list):
        """分析大盘走势"""
        try:
            # 构建分析提示
            prompt = self._build_market_prompt(market_data, news_list)
            
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一位专业的股市分析师，擅长分析大盘走势和市场情绪。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI分析大盘失败: {e}")
            return "AI分析暂时不可用"
    
    def analyze_stock(self, stock_data):
        """分析个股并给出操作建议"""
        try:
            prompt = self._build_stock_prompt(stock_data)
            
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，根据技术指标给出简洁的操作建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI分析个股失败: {e}")
            return "AI分析暂时不可用"
    
    def _build_market_prompt(self, market_data, news_list):
        """构建大盘分析提示"""
        prompt = "请根据以下信息分析今日大盘走势：\n\n"
        
        # 添加指数数据
        prompt += "大盘指数：\n"
        for name, data in market_data.items():
            if data:
                prompt += f"- {name}: {data['price']:.2f} ({data['change']:+.2f}%)\n"
        
        # 添加新闻标题
        if news_list:
            prompt += "\n重要新闻：\n"
            for i, news in enumerate(news_list[:3], 1):
                prompt += f"{i}. {news['title']}\n"
        
        prompt += "\n请给出简洁的市场分析（100字以内）和投资建议。"
        return prompt
    
    def chat(self, messages, context=""):
        """支持对话历史的聊天接口，用于钉钉机器人多轮对话"""
        try:
            system_content = (
                "你是一位专业的A股分析助手，可以查询个股行情、大盘指数、财经新闻，"
                "并给出分析建议。回答简洁专业，控制在300字以内。"
            )
            if context:
                system_content += f"\n\n以下是根据用户问题实时获取的最新市场数据，请基于此作答：\n{context}"

            full_messages = [{"role": "system", "content": system_content}] + messages

            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=full_messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"AI对话失败: {e}")
            return "AI暂时不可用，请稍后再试"

    def _build_stock_prompt(self, stock_data):
        """构建个股分析提示"""
        if not stock_data:
            return ""
        
        prompt = f"请分析以下股票：\n\n"
        prompt += f"股票名称：{stock_data['name']}({stock_data['code']})\n"
        prompt += f"当前价格：{stock_data['price']:.2f}\n"
        prompt += f"涨跌幅：{stock_data['change']:+.2f}%\n"
        prompt += f"今开：{stock_data['open']:.2f} | 最高：{stock_data['high']:.2f} | 最低：{stock_data['low']:.2f}\n"
        prompt += f"\n请给出简洁的操作建议（买入/持有/卖出）和理由（50字以内）。"
        
        return prompt
