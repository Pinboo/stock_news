"""
钉钉机器人测试脚本
用于测试钉钉webhook配置是否正确
"""
from dingtalk_bot import DingTalkBot
from datetime import datetime
import config

def test_text_message():
    """测试文本消息"""
    print("\n" + "="*50)
    print("测试1: 发送文本消息")
    print("="*50)
    
    bot = DingTalkBot()
    
    message = f"""🤖 A股智能分析系统测试

⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 如果你看到这条消息，说明钉钉机器人配置成功！

接下来系统将自动推送：
📰 财经新闻
📊 大盘行情
📈 个股分析
💡 AI投资建议

---
⚠️ 这是一条测试消息"""
    
    success = bot.send_text(message)
    
    if success:
        print("✅ 文本消息发送成功！请检查钉钉群")
    else:
        print("❌ 文本消息发送失败，请检查配置")
    
    return success

def test_markdown_message():
    """测试Markdown消息"""
    print("\n" + "="*50)
    print("测试2: 发送Markdown消息")
    print("="*50)
    
    bot = DingTalkBot()
    
    title = "A股智能分析系统"
    content = f"""### 🎯 系统测试报告

> 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#### ✅ 配置检查

- **钉钉Webhook**: {'已配置' if config.DINGTALK_WEBHOOK else '❌ 未配置'}
- **AI模型**: {'已配置' if config.OPENAI_API_KEY else '❌ 未配置'}
- **股票池**: {', '.join(config.STOCK_POOL)}

#### 📋 功能列表

1. 📰 自动抓取财经新闻
2. 📊 获取大盘实时行情
3. 📈 分析个股走势
4. 🤖 AI智能分析
5. ⏰ 定时自动推送

---

**如果看到这条消息，说明Markdown格式支持正常！**
"""
    
    success = bot.send_markdown(title, content)
    
    if success:
        print("✅ Markdown消息发送成功！请检查钉钉群")
    else:
        print("❌ Markdown消息发送失败")
    
    return success

def test_at_message():
    """测试@功能"""
    print("\n" + "="*50)
    print("测试3: 测试@功能")
    print("="*50)
    
    bot = DingTalkBot()
    
    message = """🔔 A股智能分析系统

这是一条测试@功能的消息

如果你被@了，说明@功能正常工作！"""
    
    # 注意：需要填入真实的手机号才能@到人
    # success = bot.send_text(message, at_mobiles=["13800138000"])
    
    # 或者@所有人（慎用）
    # success = bot.send_text(message, at_all=True)
    
    print("ℹ️  @功能需要手动配置手机号，请查看代码注释")
    return True

def main():
    """主测试函数"""
    print("\n" + "🚀"*25)
    print("钉钉机器人配置测试")
    print("🚀"*25)
    
    # 检测配置模式
    use_app_mode = bool(config.DINGTALK_APPKEY and config.DINGTALK_APPSECRET)
    use_webhook_mode = bool(config.DINGTALK_WEBHOOK)
    
    if not use_app_mode and not use_webhook_mode:
        print("\n❌ 错误: 钉钉配置未完成")
        print("\n请选择以下任一配置方式：")
        print("\n方式1: 自定义机器人（Webhook）- 推荐新手")
        print("  配置项: DINGTALK_WEBHOOK")
        print("\n方式2: 企业内部应用（AppKey/AppSecret）- 企业使用")
        print("  配置项: DINGTALK_APPKEY, DINGTALK_APPSECRET, DINGTALK_AGENT_ID")
        print("\n详细配置步骤请查看: DINGTALK_SETUP.md")
        return
    
    # 显示当前配置
    print("\n" + "="*50)
    print("当前配置")
    print("="*50)
    
    if use_app_mode:
        print("✅ 使用模式: 企业内部应用（AppKey/AppSecret）")
        print(f"   AppKey: {config.DINGTALK_APPKEY[:20]}...")
        print(f"   AgentId: {config.DINGTALK_AGENT_ID}")
        if config.DINGTALK_USER_IDS:
            print(f"   接收人: {config.DINGTALK_USER_IDS}")
        else:
            print(f"   接收人: 全员")
    elif use_webhook_mode:
        print("✅ 使用模式: 自定义机器人（Webhook）")
        print(f"   Webhook: {config.DINGTALK_WEBHOOK[:50]}...")
        if config.DINGTALK_SECRET:
            print(f"   加签: 已启用")
        else:
            print(f"   加签: 未启用（使用关键词或IP白名单）")
    
    # 运行测试
    results = []
    
    results.append(("文本消息", test_text_message()))
    
    import time
    time.sleep(2)  # 避免发送太快
    
    results.append(("Markdown消息", test_markdown_message()))
    
    time.sleep(2)
    
    results.append(("@功能", test_at_message()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    all_success = all(r[1] for r in results[:2])  # 前两个测试
    
    if all_success:
        print("\n🎉 恭喜！钉钉机器人配置成功！")
        print("现在可以运行 python test_run.py 测试完整功能")
    else:
        print("\n⚠️  部分测试失败，请检查:")
        if use_webhook_mode:
            print("1. Webhook地址是否正确")
            print("2. 机器人安全设置（关键词/加签/IP白名单）")
            print("3. 消息内容是否包含设置的关键词")
        else:
            print("1. AppKey和AppSecret是否正确")
            print("2. AgentId是否正确")
            print("3. 应用权限是否开通")
            print("4. 接收人是否在应用可见范围内")
        print("\n详细排查步骤请查看: DINGTALK_SETUP.md")

if __name__ == "__main__":
    main()
