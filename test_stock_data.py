"""
测试股票数据获取
对比不同数据源的效果
"""
from stock_data_v2 import StockDataV2

def test_market_data():
    """测试大盘数据"""
    print("="*50)
    print("测试大盘数据获取")
    print("="*50)
    
    stock_data = StockDataV2()
    market_data = stock_data.get_market_index()
    
    if market_data:
        print("\n✅ 获取成功！\n")
        for name, data in market_data.items():
            print(f"{name}:")
            print(f"  价格: {data['price']:.2f}")
            print(f"  涨跌: {data['change']:+.2f}%")
            print()
    else:
        print("\n❌ 获取失败")

def test_stock_data():
    """测试个股数据"""
    print("="*50)
    print("测试个股数据获取")
    print("="*50)
    
    stock_data = StockDataV2()
    
    test_codes = ['000001', '600519', '000858']
    
    for code in test_codes:
        print(f"\n测试股票: {code}")
        data = stock_data.get_stock_realtime(code)
        
        if data:
            print(f"✅ {data['name']}({code})")
            print(f"   价格: {data['price']:.2f}")
            print(f"   涨跌: {data['change']:+.2f}%")
            print(f"   今开: {data['open']:.2f}")
            print(f"   最高: {data['high']:.2f}")
            print(f"   最低: {data['low']:.2f}")
        else:
            print(f"❌ 获取失败")

def main():
    print("\n" + "🧪"*25)
    print("股票数据源测试")
    print("🧪"*25 + "\n")
    
    # 测试大盘
    test_market_data()
    
    print("\n" + "-"*50 + "\n")
    
    # 测试个股
    test_stock_data()
    
    print("\n" + "="*50)
    print("测试完成！")
    print("="*50)

if __name__ == "__main__":
    main()
