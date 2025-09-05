# 微信公众号插件 for Dify

这是一个为Dify平台开发的微信公众号插件，提供了完整的微信公众号API集成功能，支持素材管理、草稿操作和消息发布。

## 功能特性

### 🔐 访问令牌管理
- **获取访问令牌**: 获取微信公众号访问令牌，支持自动刷新
- **凭据验证**: 自动验证 App ID 和 App Secret 的有效性
- **安全存储**: 安全管理和存储访问凭据

### 📁 素材管理
- **上传永久素材**: 支持图片、语音、视频、缩略图等多种媒体类型
- **获取永久素材**: 通过媒体ID获取已上传的永久素材信息
- **删除永久素材**: 删除不再需要的永久素材
- **智能文件处理**: 自动处理文件大小限制、格式验证和错误处理
- **多种上传方式**: 支持URL链接和本地文件上传

### 📝 草稿管理
- **创建图文草稿**: 创建包含标题、内容、封面等完整信息的图文消息草稿
- **发布草稿**: 将草稿提交发布到微信公众号
- **参数验证**: 完整的参数验证和错误提示
- **中文字符支持**: 完美支持中文内容的编码和显示

## 项目结构

```
wechat_official_plugin/
├── manifest.yaml              # 插件配置文件
├── main.py                   # 插件入口文件
├── requirements.txt          # Python依赖
├── README.md                # 项目说明文档
├── .env.example             # 环境变量示例
├── _assets/
│   └── icon.svg             # 插件图标
├── provider/
│   ├── wechat_official.yaml # Provider配置
│   └── wechat_official_provider.py # Provider实现
└── tools/
    ├── __init__.py             # 工具包初始化
    ├── wechat_api_utils.py     # 微信API工具类
    ├── get_access_token.yaml   # 获取访问令牌工具配置
    ├── get_access_token.py     # 获取访问令牌工具实现
    ├── upload_material.yaml   # 上传素材工具配置
    ├── upload_material.py     # 上传素材工具实现
    ├── get_material.yaml      # 获取素材工具配置
    ├── get_material.py        # 获取素材工具实现
    ├── delete_material.yaml   # 删除素材工具配置
    ├── delete_material.py     # 删除素材工具实现
    ├── create_draft.yaml      # 创建草稿工具配置
    ├── create_draft.py        # 创建草稿工具实现
    ├── publish_draft.yaml     # 发布草稿工具配置
    └── publish_draft.py       # 发布草稿工具实现
```

## 技术规格

- **Python版本**: 3.12+
- **架构支持**: AMD64, ARM64
- **内存需求**: 1MB
- **依赖包**: 
  - `dify_plugin`: Dify插件开发框架
  - `python-dotenv>=1.0.0`: 环境变量管理
  - `Pillow>=10.0.0`: 图像处理支持

## 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.12 或更高版本。

### 2. 安装依赖

```bash
cd wechat_official_plugin
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量示例文件并配置您的微信公众号信息：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的微信公众号配置：

```env
# 微信公众号配置
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here
```

### 4. 运行插件

```bash
python main.py
```

## 插件安装

### 自定义插件本地上传

如果在安装插件时出现异常信息：
```
plugin verification has been enabled, and the plugin you want to install has a bad signature
```

**解决方案（简单粗暴）**：

直接修改 Dify 的 `.env` 文件：
```env
FORCE_VERIFYING_SIGNATURE=false
```

**注意**：添加完之后需要重启 Docker，在命令行中执行以下命令：
```bash
cd docker  # 先切换到本地 Dify 安装目录下的 docker 目录
docker compose down
docker compose up -d
```

## 配置说明

### 微信公众号配置

在使用插件之前，您需要在微信公众平台获取以下信息：

1. **App ID**: 微信公众号的应用ID
2. **App Secret**: 微信公众号的应用密钥

### 获取配置信息的步骤

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」->「基本配置」
3. 获取「开发者ID(AppID)」和「开发者密码(AppSecret)」
4. 确保公众号已认证并开通相关接口权限

### FILES_URL 配置

用于向前端展示文件预览或下载链接，或作为多模态输入；链接已签名且具有过期时间。

**文件处理插件必须配置 FILES_URL**：
- 若地址为 `https://example.com`，请设置为 `FILES_URL=https://example.com`
- 若地址为 `http://example.com`，请设置为 `FILES_URL=http://example.com`

**修改 Dify 的 `.env` 文件**：
```env
FILES_URL=http://<你的 IP 地址>
```

**重启 Docker 服务**：
```bash
docker compose down
docker compose up -d
```

## 工具使用指南

### 获取访问令牌

```python
# 获取访问令牌
result = get_access_token_tool.invoke({
    # 无需额外参数，使用配置的App ID和App Secret
})
```

### 上传素材

```python
# 上传图片素材
result = upload_material_tool.invoke({
    "media_type": "image",
    "file_url": "https://example.com/image.jpg"
})

# 上传视频素材
result = upload_material_tool.invoke({
    "media_type": "video",
    "file_url": "https://example.com/video.mp4",
    "title": "视频标题",
    "introduction": "视频描述"
})

# 上传语音素材
result = upload_material_tool.invoke({
    "media_type": "voice",
    "file_url": "https://example.com/audio.mp3"
})
```

### 获取和删除素材

```python
# 获取素材信息
result = get_material_tool.invoke({
    "media_id": "your_media_id"
})

# 删除素材
result = delete_material_tool.invoke({
    "media_id": "your_media_id"
})
```

### 创建和发布草稿

```python
# 创建图文草稿
result = create_draft_tool.invoke({
    "title": "文章标题",
    "content": "<p>文章内容HTML</p>",
    "author": "作者名称",
    "digest": "文章摘要",
    "thumb_media_id": "封面图片media_id",
    "content_source_url": "https://example.com",
    "need_open_comment": "1",
    "only_fans_can_comment": "0"
})

# 发布草稿
result = publish_draft_tool.invoke({
    "media_id": "draft_media_id"
})
```

## 错误处理

插件内置了完善的错误处理机制，包括：

- **网络错误**: 自动重试和超时处理（30秒超时）
- **API错误**: 详细的错误码解释和处理建议
- **参数验证**: 输入参数的格式和有效性检查
- **文件处理**: 文件大小、格式和权限检查
- **编码处理**: 完美支持中文字符的编码和显示
- **凭据管理**: 自动验证和刷新访问令牌

## 特色功能

### 🌟 中文字符完美支持
插件已完全解决中文字符编码问题：
- ✅ 草稿标题、内容、作者等字段完美支持中文
- ✅ JSON数据传输时正确处理Unicode字符
- ✅ 微信API响应中的中文内容正确显示
- ✅ 无需手动处理Unicode转义序列

### 🛡️ 智能参数验证
- 标题长度限制（≤64字符）
- 作者名长度限制（≤8字符）
- 摘要长度限制（≤120字符）
- 封面图片media_id格式验证
- HTML内容安全检查

## 注意事项

1. **接口权限**: 确保您的微信公众号已开通相关接口权限
2. **调用频率**: 遵守微信API的调用频率限制
3. **文件大小**: 不同类型素材有不同的文件大小限制
4. **内容审核**: 发布的内容需要通过微信平台审核
5. **原创保护**: 如有原创声明，需要通过原创审核
6. **字符编码**: 插件已自动处理中文字符编码，无需额外配置

## 故障排除

### "Invalid credentials" 错误 🔥 **最常见问题**

如果在配置插件时遇到 "Invalid credentials" 错误，请按以下步骤排查：

#### 快速诊断
```bash
# 使用内置诊断工具
python diagnostic.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET
```

#### 手动检查步骤

1. **验证凭据格式**
   - App ID: 必须以 `wx` 开头，总长度18位
   - App Secret: 必须是32位十六进制字符串
   - 确保没有多余的空格或换行符

2. **确认凭据来源**
   - 登录 [微信公众平台](https://mp.weixin.qq.com/)
   - 进入「开发」->「基本配置」
   - 复制正确的「开发者ID(AppID)」和「开发者密码(AppSecret)」

3. **检查公众号状态**
   - ✅ 公众号已完成认证
   - ✅ 已开通素材管理接口权限
   - ✅ 已开通草稿箱/发布接口权限

4. **网络连接测试**
   ```bash
   # 测试是否能访问微信API
   curl -I https://api.weixin.qq.com
   ```

#### 常见错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40013 | 不合法的AppID | 检查App ID格式和有效性 |
| 41004 | 缺少secret参数 | 确认App Secret已正确填写 |
| 42001 | access_token超时 | 重新获取访问令牌 |
| 48001 | api功能未授权 | 确认公众号已开通相关接口权限 |

**详细故障排除指南**: 请参阅 [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md)

## 技术支持

如果您在使用过程中遇到问题，请检查：

1. 微信公众号配置是否正确
2. 网络连接是否正常
3. API权限是否已开通
4. 调用参数是否符合要求

### 获取帮助

1. **运行诊断工具**: `python diagnostic.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET`
2. **查看详细日志**: 检查 Dify 系统日志中的错误信息
3. **参考文档**: 查看 [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) 获取详细解决方案

## 更新日志

### v0.0.1 (2025-09-05)
- 🎉 初始版本发布
- ✅ 支持访问令牌获取和管理
- ✅ 支持永久素材上传、获取、删除
- ✅ 支持图文草稿创建和发布
- ✅ 完整的错误处理和参数验证机制
- ✅ 修复中文字符编码问题，完美支持Unicode
- ✅ 智能文件处理和格式验证
- ✅ 30秒超时设置适配微信API响应时间
- ✅ 详细的错误诊断和用户友好的错误提示

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。