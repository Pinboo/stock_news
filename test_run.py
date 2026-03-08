"""
测试脚本 - 立即执行一次分析，不等待定时任务
"""
from main import StockAnalysisSystem

if __name__ == "__main__":
    print("🧪 开始测试运行...\n")
    system = StockAnalysisSystem()
    system.run_analysis()
    print("\n✅ 测试完成！")
