"""
获取钉钉用户ID的辅助工具
用于企业应用模式下获取接收人的UserId
"""
import requests
import config

def get_access_token():
    """获取access_token"""
    url = "https://oapi.dingtalk.com/gettoken"
    params = {
        "appkey": config.DINGTALK_APPKEY,
        "appsecret": config.DINGTALK_APPSECRET
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if result.get('errcode') == 0:
            return result['access_token']
        else:
            print(f"❌ 获取access_token失败: {result}")
            return None
    except Exception as e:
        print(f"❌ 获取access_token异常: {e}")
        return None

def get_user_id_by_mobile(mobile):
    """通过手机号获取用户ID"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    url = f"https://oapi.dingtalk.com/topapi/v2/user/getbymobile?access_token={access_token}"
    data = {"mobile": mobile}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('errcode') == 0:
            user_info = result['result']
            return {
                'userid': user_info['userid'],
                'name': user_info.get('name', ''),
                'mobile': mobile
            }
        else:
            print(f"❌ 获取用户信息失败: {result}")
            return None
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return None

def get_department_users(dept_id=1):
    """获取部门用户列表"""
    access_token = get_access_token()
    if not access_token:
        return []
    
    url = f"https://oapi.dingtalk.com/topapi/v2/user/list?access_token={access_token}"
    data = {
        "dept_id": dept_id,
        "cursor": 0,
        "size": 100
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('errcode') == 0:
            users = result['result']['list']
            return [{
                'userid': user['userid'],
                'name': user['name'],
                'mobile': user.get('mobile', '')
            } for user in users]
        else:
            print(f"❌ 获取部门用户失败: {result}")
            return []
    except Exception as e:
        print(f"❌ 获取部门用户异常: {e}")
        return []

def main():
    """主函数"""
    print("\n" + "="*50)
    print("钉钉用户ID查询工具")
    print("="*50)
    
    # 检查配置
    if not config.DINGTALK_APPKEY or not config.DINGTALK_APPSECRET:
        print("\n❌ 错误: 企业应用配置未完成")
        print("请在 .env 文件中配置:")
        print("  - DINGTALK_APPKEY")
        print("  - DINGTALK_APPSECRET")
        return
    
    print("\n请选择查询方式:")
    print("1. 通过手机号查询")
    print("2. 查看部门所有用户")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        mobile = input("请输入手机号: ").strip()
        print(f"\n正在查询手机号 {mobile} 的用户信息...")
        
        user_info = get_user_id_by_mobile(mobile)
        if user_info:
            print("\n✅ 查询成功！")
            print(f"   用户ID: {user_info['userid']}")
            print(f"   姓名: {user_info['name']}")
            print(f"   手机: {user_info['mobile']}")
            print(f"\n请将以下内容添加到 .env 文件:")
            print(f"DINGTALK_USER_IDS={user_info['userid']}")
        else:
            print("\n❌ 查询失败，请检查手机号是否正确")
    
    elif choice == "2":
        dept_id = input("请输入部门ID (直接回车默认为根部门): ").strip()
        dept_id = int(dept_id) if dept_id else 1
        
        print(f"\n正在查询部门 {dept_id} 的用户列表...")
        
        users = get_department_users(dept_id)
        if users:
            print(f"\n✅ 查询成功！共找到 {len(users)} 个用户:\n")
            
            for i, user in enumerate(users, 1):
                print(f"{i}. {user['name']}")
                print(f"   用户ID: {user['userid']}")
                print(f"   手机: {user['mobile']}")
                print()
            
            print("如需指定接收人，请将用户ID添加到 .env 文件:")
            user_ids = ','.join([u['userid'] for u in users[:3]])
            print(f"DINGTALK_USER_IDS={user_ids}")
        else:
            print("\n❌ 查询失败")
    
    else:
        print("\n❌ 无效的选项")

if __name__ == "__main__":
    main()
