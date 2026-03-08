"""
股票数据获取器 V2 - 多数据源支持
支持：Baostock（优先）、新浪财经、腾讯财经、Tushare、东方财富
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta
import config

class StockDataV2:
    """股票数据获取器（多数据源）"""
    
    def __init__(self):
        self.max_retries = 2
        self.retry_delay = 1
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 初始化 Baostock
        self.baostock_available = False
        try:
            import baostock as bs
            lg = bs.login()
            if lg.error_code == '0':
                self.bs = bs
                self.baostock_available = True
                print("   ✓ Baostock 已启用（免费无限制）")
        except Exception as e:
            print(f"   ⚠️  Baostock 初始化失败: {str(e)[:50]}")
        
        # 初始化 Tushare
        self.tushare_available = False
        if config.TUSHARE_TOKEN:
            try:
                import tushare as ts
                ts.set_token(config.TUSHARE_TOKEN)
                self.ts_pro = ts.pro_api()
                self.tushare_available = True
                print("   ✓ Tushare 已启用")
            except Exception as e:
                print(f"   ⚠️  Tushare 初始化失败: {str(e)[:50]}")
    
    def __del__(self):
        """析构函数，登出 Baostock"""
        if self.baostock_available:
            try:
                self.bs.logout()
            except:
                pass
    
    def get_market_index(self):
        """获取大盘指数数据（多数据源）"""
        # 数据源优先级：Baostock > 腾讯 > 新浪 > Tushare > 东方财富
        sources = []
        
        if self.baostock_available:
            sources.append(self._get_market_from_baostock)
        
        sources.extend([
            self._get_market_from_tencent,
            self._get_market_from_sina,
        ])
        
        if self.tushare_available:
            sources.append(self._get_market_from_tushare)
        
        sources.append(self._get_market_from_eastmoney)
        
        for source_func in sources:
            try:
                result = source_func()
                if result:
                    return result
            except Exception as e:
                print(f"   数据源失败: {str(e)[:50]}")
                continue
        
        # 所有数据源都失败，返回备用数据
        return self._get_fallback_market_data()
    
    def _get_market_from_baostock(self):
        """从 Baostock 获取大盘数据"""
        print("   尝试 Baostock...")
        
        try:
            codes = {
                'sh.000001': '上证指数',
                'sz.399001': '深证成指',
                'sz.399006': '创业板指'
            }
            
            result = {}
            today = datetime.now().strftime('%Y-%m-%d')
            
            for code, name in codes.items():
                try:
                    # 获取最近的交易日数据
                    rs = self.bs.query_history_k_data_plus(
                        code,
                        "date,code,close,pctChg",
                        start_date=today,
                        end_date=today,
                        frequency="d"
                    )
                    
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())
                    
                    if not data_list:
                        # 如果今天没数据，获取最近5天的
                        start = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
                        rs = self.bs.query_history_k_data_plus(
                            code,
                            "date,code,close,pctChg",
                            start_date=start,
                            end_date=today,
                            frequency="d"
                        )
                        while (rs.error_code == '0') & rs.next():
                            data_list.append(rs.get_row_data())
                    
                    if data_list:
                        latest = data_list[-1]
                        close = float(latest[2])
                        pct_chg = float(latest[3]) if latest[3] else 0
                        
                        result[name] = {
                            'code': code,
                            'name': name,
                            'price': close,
                            'change': pct_chg,
                            'volume': 0
                        }
                        print(f"   ✓ {name}: {close:.2f} ({pct_chg:+.2f}%)")
                except Exception as e:
                    continue
            
            return result if result else None
        except Exception as e:
            print(f"   Baostock 失败: {str(e)[:50]}")
            return None
    
    def _get_market_from_tushare(self):
        """从 Tushare 获取大盘数据"""
        print("   尝试 Tushare...")
        
        try:
            # 获取指数实时行情
            codes = {
                '000001.SH': '上证指数',
                '399001.SZ': '深证成指',
                '399006.SZ': '创业板指'
            }
            
            result = {}
            
            for ts_code, name in codes.items():
                try:
                    # 获取最新行情
                    df = self.ts_pro.index_daily(ts_code=ts_code, trade_date='')
                    
                    if df.empty:
                        # 如果没有数据，尝试获取最近一个交易日
                        df = self.ts_pro.index_daily(ts_code=ts_code)
                    
                    if not df.empty:
                        row = df.iloc[0]
                        close = row['close']
                        pct_chg = row['pct_chg']
                        
                        result[name] = {
                            'code': ts_code,
                            'name': name,
                            'price': close,
                            'change': pct_chg,
                            'volume': row.get('vol', 0)
                        }
                        print(f"   ✓ {name}: {close:.2f} ({pct_chg:+.2f}%)")
                except Exception as e:
                    continue
            
            return result if result else None
        except Exception as e:
            print(f"   Tushare 失败: {str(e)[:50]}")
            return None
    
    def _get_market_from_sina(self):
        """从新浪财经获取大盘数据"""
        print("   尝试新浪财经...")
        
        # 新浪财经接口
        codes = {
            's_sh000001': '上证指数',
            's_sz399001': '深证成指',
            's_sz399006': '创业板指'
        }
        
        url = f"http://hq.sinajs.cn/list={','.join(codes.keys())}"
        
        response = requests.get(url, headers=self.headers, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code != 200:
            return None
        
        result = {}
        lines = response.text.strip().split('\n')
        
        for line in lines:
            if 'hq_str_' not in line:
                continue
            
            code = line.split('hq_str_')[1].split('=')[0]
            data_str = line.split('"')[1]
            
            if not data_str:
                continue
            
            parts = data_str.split(',')
            if len(parts) < 4:
                continue
            
            name = codes.get(code, code)
            current = float(parts[1]) if parts[1] else 0
            prev_close = float(parts[2]) if parts[2] else 0
            
            if prev_close > 0:
                change = ((current - prev_close) / prev_close) * 100
            else:
                change = 0
            
            result[name] = {
                'code': code,
                'name': name,
                'price': current,
                'change': change,
                'volume': 0
            }
            
            print(f"   ✓ {name}: {current:.2f} ({change:+.2f}%)")
        
        return result if result else None
    
    def _get_market_from_tencent(self):
        """从腾讯财经获取大盘数据"""
        print("   尝试腾讯财经...")
        
        codes = {
            's_sh000001': '上证指数',
            's_sz399001': '深证成指',
            's_sz399006': '创业板指'
        }
        
        url = f"http://qt.gtimg.cn/q={','.join(codes.keys())}"
        
        response = requests.get(url, headers=self.headers, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code != 200:
            return None
        
        result = {}
        lines = response.text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split('~')
            if len(parts) < 6:
                continue
            
            code = parts[0].split('_')[-1]
            name = codes.get(f"s_{code}", parts[1])
            current = float(parts[3]) if parts[3] else 0
            change = float(parts[32]) if len(parts) > 32 and parts[32] else 0
            
            result[name] = {
                'code': code,
                'name': name,
                'price': current,
                'change': change,
                'volume': 0
            }
            
            print(f"   ✓ {name}: {current:.2f} ({change:+.2f}%)")
        
        return result if result else None
    
    def _get_market_from_eastmoney(self):
        """从东方财富获取大盘数据"""
        print("   尝试东方财富...")
        
        try:
            import akshare as ak
            df = ak.stock_zh_index_spot_em()
            
            if df.empty:
                return None
            
            result = {}
            
            for index_name in ['上证指数', '深证成指', '创业板指']:
                data = df[df['名称'].str.contains(index_name, na=False)]
                if not data.empty:
                    row = data.iloc[0]
                    result[index_name] = {
                        'code': row.get('代码', ''),
                        'name': index_name,
                        'price': row.get('最新价', 0),
                        'change': row.get('涨跌幅', 0),
                        'volume': row.get('成交量', 0)
                    }
                    print(f"   ✓ {index_name}")
            
            return result if result else None
        except:
            return None
    
    def search_stock_code(self, name):
        """根据股票名称模糊搜索股票代码，返回第一个匹配的代码，找不到返回 None"""
        try:
            url = f"http://suggest3.sinajs.cn/suggest/type=11,12&key={name}"
            resp = requests.get(url, headers=self.headers, timeout=5)
            resp.encoding = 'gbk'
            text = resp.text
            # 格式: var suggestvalue="股票名,type,code,..."
            if 'suggestvalue="' in text:
                content = text.split('suggestvalue="')[1].split('"')[0]
                if content:
                    first = content.split(';')[0]
                    parts = first.split(',')
                    if len(parts) >= 3:
                        return parts[2]  # 股票代码
        except Exception:
            pass
        return None

    def get_stock_realtime(self, stock_code):
        """获取个股实时行情（多数据源）"""
        # 数据源优先级：Baostock > 腾讯 > 新浪 > Tushare > 东方财富
        sources = []
        
        if self.baostock_available:
            sources.append(lambda: self._get_stock_from_baostock(stock_code))
        
        sources.extend([
            lambda: self._get_stock_from_tencent(stock_code),
            lambda: self._get_stock_from_sina(stock_code),
        ])
        
        if self.tushare_available:
            sources.append(lambda: self._get_stock_from_tushare(stock_code))
        
        sources.append(lambda: self._get_stock_from_eastmoney(stock_code))
        
        for source_func in sources:
            try:
                result = source_func()
                if result:
                    return result
            except Exception as e:
                continue
        
        return None
    
    def _get_stock_from_baostock(self, stock_code):
        """从 Baostock 获取个股数据"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                bs_code = f"sh.{stock_code}"
            else:
                bs_code = f"sz.{stock_code}"
            
            today = datetime.now().strftime('%Y-%m-%d')
            start = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
            
            # 获取K线数据
            rs = self.bs.query_history_k_data_plus(
                bs_code,
                "date,code,open,high,low,close,pctChg,volume,amount",
                start_date=start,
                end_date=today,
                frequency="d",
                adjustflag="3"
            )
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            # 获取最新数据
            latest = data_list[-1]
            
            # 获取股票名称
            rs_name = self.bs.query_stock_basic(code=bs_code)
            name = stock_code
            if rs_name.error_code == '0':
                while rs_name.next():
                    row = rs_name.get_row_data()
                    name = row[2]  # code_name
                    break
            
            return {
                'code': stock_code,
                'name': name,
                'price': float(latest[5]),  # close
                'change': float(latest[6]) if latest[6] else 0,  # pctChg
                'volume': float(latest[7]) if latest[7] else 0,  # volume
                'amount': float(latest[8]) if latest[8] else 0,  # amount
                'high': float(latest[3]),  # high
                'low': float(latest[4]),  # low
                'open': float(latest[2])  # open
            }
        except Exception as e:
            return None
    
    def _get_stock_from_tushare(self, stock_code):
        """从 Tushare 获取个股数据"""
        try:
            # 转换股票代码格式
            if stock_code.startswith('6'):
                ts_code = f"{stock_code}.SH"
            else:
                ts_code = f"{stock_code}.SZ"
            
            # 获取最新行情
            df = self.ts_pro.daily(ts_code=ts_code, trade_date='')
            
            if df.empty:
                df = self.ts_pro.daily(ts_code=ts_code)
            
            if df.empty:
                return None
            
            row = df.iloc[0]
            
            # 获取股票名称
            name_df = self.ts_pro.stock_basic(ts_code=ts_code, fields='ts_code,name')
            name = name_df.iloc[0]['name'] if not name_df.empty else stock_code
            
            return {
                'code': stock_code,
                'name': name,
                'price': row['close'],
                'change': row['pct_chg'],
                'volume': row['vol'],
                'amount': row['amount'],
                'high': row['high'],
                'low': row['low'],
                'open': row['open']
            }
        except Exception as e:
            return None
    
    def _get_stock_from_sina(self, stock_code):
        """从新浪财经获取个股数据"""
        # 判断股票代码前缀
        if stock_code.startswith('6'):
            prefix = 'sh'
        else:
            prefix = 'sz'
        
        code = f"{prefix}{stock_code}"
        url = f"http://hq.sinajs.cn/list={code}"
        
        response = requests.get(url, headers=self.headers, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code != 200:
            return None
        
        data_str = response.text.split('"')[1]
        if not data_str:
            return None
        
        parts = data_str.split(',')
        if len(parts) < 32:
            return None
        
        name = parts[0]
        open_price = float(parts[1])
        prev_close = float(parts[2])
        current = float(parts[3])
        high = float(parts[4])
        low = float(parts[5])
        volume = float(parts[8])
        amount = float(parts[9])
        
        if prev_close > 0:
            change = ((current - prev_close) / prev_close) * 100
        else:
            change = 0
        
        return {
            'code': stock_code,
            'name': name,
            'price': current,
            'change': change,
            'volume': volume,
            'amount': amount,
            'high': high,
            'low': low,
            'open': open_price
        }
    
    def _get_stock_from_tencent(self, stock_code):
        """从腾讯财经获取个股数据"""
        if stock_code.startswith('6'):
            prefix = 'sh'
        else:
            prefix = 'sz'
        
        code = f"{prefix}{stock_code}"
        url = f"http://qt.gtimg.cn/q={code}"
        
        response = requests.get(url, headers=self.headers, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code != 200:
            return None
        
        parts = response.text.split('~')
        if len(parts) < 50:
            return None
        
        return {
            'code': stock_code,
            'name': parts[1],
            'price': float(parts[3]),
            'change': float(parts[32]),
            'volume': float(parts[6]),
            'amount': float(parts[37]),
            'high': float(parts[33]),
            'low': float(parts[34]),
            'open': float(parts[5])
        }
    
    def _get_stock_from_eastmoney(self, stock_code):
        """从东方财富获取个股数据"""
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == stock_code]
            
            if stock_data.empty:
                return None
            
            row = stock_data.iloc[0]
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
        except:
            return None
    
    def _get_fallback_market_data(self):
        """获取备用数据"""
        print("   ℹ️  所有数据源失败，使用备用数据")
        return {
            '上证指数': {
                'code': '000001',
                'name': '上证指数',
                'price': 3000.0,
                'change': 0.0,
                'volume': 0
            },
            '深证成指': {
                'code': '399001',
                'name': '深证成指',
                'price': 10000.0,
                'change': 0.0,
                'volume': 0
            }
        }
    
    def format_market_data(self, market_data):
        """格式化大盘数据"""
        if not market_data:
            return "⚠️  暂无大盘数据"
        
        text = "📊 大盘行情\n\n"
        for name, data in market_data.items():
            if data:
                if data['change'] > 0:
                    emoji = "📈"
                elif data['change'] < 0:
                    emoji = "📉"
                else:
                    emoji = "➡️"
                
                text += f"{emoji} {name}: {data['price']:.2f} ({data['change']:+.2f}%)\n"
        
        return text
    
    def format_stock_data(self, stock_data):
        """格式化个股数据"""
        if not stock_data:
            return ""
        
        if stock_data['change'] > 0:
            emoji = "📈"
        elif stock_data['change'] < 0:
            emoji = "📉"
        else:
            emoji = "➡️"
        
        text = f"{emoji} {stock_data['name']}({stock_data['code']})\n"
        text += f"   价格: {stock_data['price']:.2f} ({stock_data['change']:+.2f}%)\n"
        text += f"   今开: {stock_data['open']:.2f} | 最高: {stock_data['high']:.2f} | 最低: {stock_data['low']:.2f}\n"
        
        return text
