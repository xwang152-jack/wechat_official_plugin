# 微信公众号插件故障排除指南

## 问题：在Dify中显示 "Invalid credentials"

### 问题原因分析

当在Dify中安装微信公众号插件后显示"Invalid credentials"错误时，通常是以下原因之一：

### 1. 凭据配置问题

#### 检查App ID和App Secret
- **App ID格式**：通常是以`wx`开头的18位字符串，例如：`wxd229b12345678901`
- **App Secret格式**：32位字符串，例如：`e644e5b3f1234567890abcdef1234567`

#### 获取正确的凭据
1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入「开发」→「基本配置」
3. 查看「开发者ID(AppID)」和「开发者密码(AppSecret)」

### 2. 微信公众号状态问题

#### 确认公众号类型
- ✅ **服务号**：支持所有API功能
- ✅ **订阅号（认证）**：支持大部分API功能
- ❌ **订阅号（未认证）**：API功能受限
- ❌ **个人订阅号**：不支持大部分API功能

#### 确认认证状态
- 在微信公众平台查看账号是否已完成微信认证
- 未认证的公众号无法使用stable_token接口

### 3. API权限问题

#### 检查接口权限
1. 登录微信公众平台
2. 进入「开发」→「接口权限」
3. 确认以下接口已开通：
   - 基础支持 → 获取access_token
   - 素材管理 → 新增临时素材、新增永久素材等

### 4. 网络连接问题

#### 检查网络连接
- 确保服务器能够访问微信API域名：`api.weixin.qq.com`
- 检查防火墙设置是否阻止了HTTPS请求
- 确认DNS解析正常

### 5. 测试步骤

#### 步骤1：验证凭据格式
```bash
# 在插件目录下运行测试脚本
python test_provider_simple.py
```

#### 步骤2：手动测试API调用
```bash
# 使用curl测试微信API
curl -X POST "https://api.weixin.qq.com/cgi-bin/stable_token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credential",
    "appid": "你的AppID",
    "secret": "你的AppSecret",
    "force_refresh": false
  }'
```

预期返回：
```json
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

### 6. 常见错误码及解决方案

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| 40013 | 不合法的AppID | 检查AppID是否正确，确认复制时没有多余空格 |
| 40001 | AppSecret错误 | 检查AppSecret是否正确，可以重新生成 |
| 48001 | api功能未授权 | 确认公众号已认证，接口权限已开通 |
| 41002 | 缺少appid参数 | 检查参数名称是否正确 |
| 41004 | 缺少secret参数 | 检查参数名称是否正确 |

### 7. 在Dify中正确配置

#### 配置步骤
1. 在Dify中进入「工具」→「自定义工具」
2. 找到「微信公众号」插件
3. 点击「配置」
4. 填入正确的凭据：
   - **App ID**：从微信公众平台获取的AppID
   - **App Secret**：从微信公众平台获取的AppSecret
5. 点击「保存」

#### 注意事项
- 确保输入时没有多余的空格
- App Secret是敏感信息，输入后会被隐藏
- 如果之前配置过，可能需要重新输入App Secret

### 8. 如果问题仍然存在

#### 检查插件日志
1. 查看Dify的插件日志
2. 寻找具体的错误信息
3. 根据错误信息进行针对性排查

#### 联系支持
如果按照以上步骤仍无法解决问题，请提供以下信息：
- 微信公众号类型（服务号/订阅号）
- 认证状态
- 具体的错误信息
- 测试脚本的输出结果

---

**重要提醒**：
- 请勿在公开场合分享App Secret
- 定期更换App Secret以确保安全
- 确保服务器时间准确，时间偏差可能导致API调用失败