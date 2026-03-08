# 钉钉机器人接入指南

本系统支持两种钉钉接入方式，可根据需求选择：

## 方式对比

| 特性 | 自定义机器人（Webhook） | 企业内部应用（AppKey/AppSecret） |
|------|----------------------|--------------------------------|
| 配置难度 | ⭐ 简单 | ⭐⭐⭐ 较复杂 |
| 使用场景 | 群聊推送 | 工作通知、个人消息 |
| 权限要求 | 群主/管理员 | 企业管理员 |
| 消息限制 | 20条/分钟 | 更高频率 |
| 功能丰富度 | 基础 | 高级（支持更多API） |
| 推荐场景 | 快速测试、小团队 | 企业正式使用 |

---

# 方式一：自定义机器人（Webhook）⭐ 推荐新手

## 一、创建钉钉群机器人

### 1. 进入群设置
- 打开钉钉，进入你想接收消息的群聊
- 点击右上角 `···` → `智能群助手` → `添加机器人`

### 2. 选择机器人类型
- 选择 `自定义` 机器人
- 点击 `添加`

### 3. 配置机器人
- **机器人名称**：填写 `A股智能分析助手`（或自定义名称）
- **安全设置**：选择以下任一方式
  
  **方式一：自定义关键词（推荐）**
  - 勾选 `自定义关键词`
  - 填写关键词：`A股` 或 `分析` 或 `行情`
  - 系统会自动在消息中包含这些关键词
  
  **方式二：加签**
  - 勾选 `加签`
  - 复制密钥（后面配置需要用到）
  
  **方式三：IP地址（白名单）**
  - 勾选 `IP地址（段）`
  - 填写服务器的公网IP

### 4. 获取 Webhook 地址
- 点击 `完成`
- 复制生成的 Webhook 地址，格式如下：
  ```
  https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxx
  ```

---

## 二、配置到系统

### 方式一：使用自定义关键词（最简单）

在 `.env` 文件中配置：

```env
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=你的token
```

系统已自动在消息中包含 "A股" 关键词，无需额外配置。

### 方式二：使用加签（更安全）

如果你选择了加签方式，需要修改代码：

1. 在 `.env` 中添加密钥：
```env
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=你的token
DINGTALK_SECRET=SEC开头的密钥
```

2. 更新 `config.py`：
```python
DINGTALK_SECRET = os.getenv('DINGTALK_SECRET', '')
```

3. 更新 `dingtalk_bot.py`（使用下面提供的增强版本）

---

## 三、测试机器人

运行测试脚本：

```bash
python test_dingtalk.py
```

如果配置正确，你会在钉钉群里收到测试消息。

---

## 四、常见问题

### 1. 发送失败：关键词不匹配
**错误信息**：`errcode: 310000`

**解决方案**：
- 检查机器人安全设置中的关键词
- 确保消息内容包含至少一个关键词
- 系统默认在标题中包含 "A股"，如果你设置了其他关键词，需要修改代码

### 2. 发送失败：签名验证失败
**错误信息**：`errcode: 310000, sign not match`

**解决方案**：
- 检查 `DINGTALK_SECRET` 是否正确
- 确保使用了加签版本的代码

### 3. 发送失败：IP不在白名单
**错误信息**：`errcode: 310000`

**解决方案**：
- 在钉钉机器人设置中添加服务器IP到白名单
- 或改用关键词/加签方式

### 4. 消息发送频率限制
钉钉机器人限制：
- 每个机器人每分钟最多发送 20 条消息
- 建议设置合理的推送时间间隔

---

## 五、消息格式说明

系统支持两种消息格式：

### 1. 文本消息（当前使用）
```python
dingtalk_bot.send_text("消息内容")
```

### 2. Markdown消息（更美观）
```python
dingtalk_bot.send_markdown("标题", "Markdown内容")
```

可以在 `main.py` 中切换使用。

---

## 六、进阶配置

### 多群推送
如果需要推送到多个群，在 `.env` 中配置多个webhook（用逗号分隔）：

```env
DINGTALK_WEBHOOK=webhook1,webhook2,webhook3
```

然后修改 `dingtalk_bot.py` 支持多webhook发送。

### @指定成员
在消息中 @特定成员：

```python
data = {
    "msgtype": "text",
    "text": {
        "content": "消息内容"
    },
    "at": {
        "atMobiles": ["13800138000"],  # 手机号
        "isAtAll": False  # 是否@所有人
    }
}
```

---

## 七、安全建议

1. ✅ 不要将 Webhook 地址提交到公开代码仓库
2. ✅ 使用 `.env` 文件管理敏感信息
3. ✅ 建议使用加签方式，安全性更高
4. ✅ 定期更换 access_token
5. ✅ 设置合理的消息发送频率

---

## 八、钉钉机器人文档

官方文档：https://open.dingtalk.com/document/robots/custom-robot-access

---
---

# 方式二：企业内部应用（AppKey/AppSecret）

适合企业正式使用，功能更强大，支持发送工作通知到个人。

## 一、创建企业内部应用

### 1. 进入钉钉开发者后台
- 访问：https://open-dev.dingtalk.com/
- 使用管理员账号登录

### 2. 创建应用
- 点击左侧 `应用开发` → `企业内部开发`
- 点击 `创建应用`
- 填写应用信息：
  - **应用名称**：A股智能分析系统
  - **应用描述**：自动推送股市分析报告
  - **应用图标**：上传一个图标（可选）

### 3. 获取凭证
创建成功后，在应用详情页可以看到：
- **AppKey**（也叫ClientId）
- **AppSecret**（也叫ClientSecret）
- **AgentId**

### 4. 配置权限
在应用管理页面：
- 点击 `权限管理`
- 开通以下权限：
  - ✅ 企业内部应用免登
  - ✅ 通讯录只读权限
  - ✅ 消息通知

### 5. 配置可见范围
- 点击 `可见范围`
- 添加需要接收消息的员工或部门
- 或设置为 `全员可见`

---

## 二、配置到系统

在 `.env` 文件中配置：

```env
# 使用企业应用方式（配置这些后，WEBHOOK可以不配置）
DINGTALK_APPKEY=dingxxxxxxxxxxxxx
DINGTALK_APPSECRET=your_app_secret
DINGTALK_AGENT_ID=123456789

# 可选：指定接收人（用户ID，逗号分隔）
# 留空则发给所有可见范围内的人
DINGTALK_USER_IDS=user001,user002
```

---

## 三、获取用户ID

如果需要指定接收人，需要获取用户的 UserId：

### 方法1: 通过API获取
```python
import requests

def get_user_id_by_mobile(access_token, mobile):
    """通过手机号获取用户ID"""
    url = f"https://oapi.dingtalk.com/topapi/v2/user/getbymobile?access_token={access_token}"
    data = {"mobile": mobile}
    response = requests.post(url, json=data)
    result = response.json()
    if result.get('errcode') == 0:
        return result['result']['userid']
    return None
```

### 方法2: 在管理后台查看
- 进入钉钉管理后台
- 通讯录 → 选择员工 → 查看详情
- 可以看到员工的 UserId

---

## 四、测试企业应用

运行测试脚本：

```bash
python test_dingtalk.py
```

系统会自动检测配置方式并使用对应的API。

---

## 五、两种方式的区别

### Webhook方式（自定义机器人）
```
优点：
✅ 配置简单，5分钟搞定
✅ 不需要企业管理员权限
✅ 适合快速测试

缺点：
❌ 只能发到群聊
❌ 需要配置安全设置（关键词/加签/IP）
❌ 频率限制较严格（20条/分钟）
```

### AppKey/AppSecret方式（企业应用）
```
优点：
✅ 可以发送工作通知到个人
✅ 支持更多高级功能
✅ 频率限制更宽松
✅ 更适合企业正式使用
✅ 可以精确控制接收人

缺点：
❌ 配置较复杂
❌ 需要企业管理员权限
❌ 需要在开发者后台创建应用
```

---

## 六、常见问题（企业应用）

### 1. 获取access_token失败
**错误信息**：`errcode: 40001`

**解决方案**：
- 检查 AppKey 和 AppSecret 是否正确
- 确认应用状态是否为"已发布"

### 2. 发送消息失败：无权限
**错误信息**：`errcode: 60011`

**解决方案**：
- 检查应用权限是否开通"消息通知"
- 确认接收人在应用的可见范围内

### 3. 用户收不到消息
**可能原因**：
- 用户不在应用的可见范围内
- DINGTALK_USER_IDS 配置的用户ID不正确
- 应用未发布或未启用

**解决方案**：
- 在应用管理后台检查可见范围
- 使用正确的 UserId（不是手机号）
- 确认应用已发布

---

## 七、推荐配置

### 个人学习/测试
使用 **Webhook方式**，配置简单快速

### 小团队使用
使用 **Webhook方式**，发到专门的股票分析群

### 企业正式使用
使用 **AppKey/AppSecret方式**，发送工作通知到个人

---

## 八、相关文档

- 自定义机器人：https://open.dingtalk.com/document/robots/custom-robot-access
- 企业内部应用：https://open.dingtalk.com/document/orgapp/develop-org-internal-apps
- 工作通知API：https://open.dingtalk.com/document/orgapp/asynchronous-sending-of-enterprise-session-messages
