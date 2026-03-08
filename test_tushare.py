"""
测试 Tushare 配置
"""
import config

def test_tushare_token():
    """测试 Tushare Token"""
    print("="*50)
    print("测试 Tushare 配置")
    print("="*50)
    
    if not config.TUSHARE_TOKEN:
        print("\n❌ Tushare Token 未配置")
        print("\n配置步骤：")
        print("1. 访问 https://tushare.pro/register 注册")
        print("2. 登录后在个人主页获取 Token")
        print("3. 在 .env 文件中配置:")
        print("   TUSHARE_TOKEN=你的Token")
        print("\n详细说明请查看: Tushare配置指南.md")
        return False
    
    print(f"\n✅ Token 已配置: {config.TUSHARE_TOKEN[:20]}...")
    
    try:
        import tushare as ts
        print("✅ Tushare 库已安装")
        
        # 设置 Token
        ts.set_token(config.TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        print("✅ Token 设置成功")
        
        # 测试获取数据
        print("\n测试获取上证指数数据...")
        df = pro.index_daily(ts_code='000001.SH')
        
        if not df.empty:
            print("✅ 数据获取成功！")
            print(f"\n最新数据:")
            row = df.iloc[0]
            print(f"  日期: {row['trade_date']}")
            print(f"  收盘: {row['close']:.2f}")
            print(f"  涨跌: {row['pct_chg']:+.2f}%")
            
            print("\n" + "="*50)
            print("🎉 Tushare 配置成功！")
            print("="*50)
            print("\n现在可以使用最稳定的数据源了！")
            return True
        else:
            print("⚠️  未获取到数据，可能是:")
            print("  1. Token 权限不足")
            print("  2. 网络问题")
            print("  3. 非交易日")
            return False
            
    except ImportError:
        print("\n❌ Tushare 库未安装")
        print("\n安装命令:")
        print("  pip install tushare")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("\n可能的原因:")
        print("  1. Token 错误")
        print("  2. 网络问题")
        print("  3. Token 未激活")
        print("\n解决方案:")
        print("  1. 检查 Token 是否正确")
        print("  2. 访问 https://tushare.pro/ 确认账号状态")
        return False

def main():
    print("\n" + "🧪"*25)
    print("Tushare 配置测试")
    print("🧪"*25 + "\n")
    
    success = test_tushare_token()
    
    if not success:
        print("\n" + "="*50)
        print("💡 提示")
        print("="*50)
        print("\n即使不配置 Tushare，系统也能正常运行")
        print("会自动使用其他数据源（新浪、腾讯）")
        print("\n但 Tushare 数据更稳定，推荐配置！")
        print("\n详细配置请查看: Tushare配置指南.md")

if __name__ == "__main__":
    main()
