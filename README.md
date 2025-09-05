# WeChat Official Account Plugin for Dify

This is a WeChat Official Account plugin developed for the Dify platform, providing complete WeChat Official Account API integration with support for material management, draft operations, and message publishing.

## Features

### 🔐 Access Token Management
- **Get Access Token**: Retrieve WeChat Official Account access tokens with automatic refresh support
- **Credential Validation**: Automatically validate App ID and App Secret validity
- **Secure Storage**: Securely manage and store access credentials

### 📁 Material Management
- **Upload Permanent Materials**: Support for multiple media types including images, audio, video, and thumbnails
- **Get Permanent Materials**: Retrieve uploaded permanent material information using media IDs
- **Delete Permanent Materials**: Remove unnecessary permanent materials
- **Smart File Processing**: Automatic handling of file size limits, format validation, and error processing
- **Multiple Upload Methods**: Support for both URL links and local file uploads

### 📝 Draft Management
- **Create Article Drafts**: Create article message drafts with complete information including titles, content, and cover images
- **Publish Drafts**: Submit drafts for publication to WeChat Official Account
- **Parameter Validation**: Complete parameter validation and error prompts
- **Chinese Character Support**: Perfect support for Chinese content encoding and display

## Project Structure

```
wechat_official_plugin/
├── manifest.yaml              # Plugin configuration file
├── main.py                   # Plugin entry file
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── .env.example             # Environment variable example
├── _assets/
│   └── icon.svg             # Plugin icon
├── provider/
│   ├── wechat_official.yaml # Provider configuration
│   └── wechat_official_provider.py # Provider implementation
└── tools/
    ├── __init__.py             # Tool package initialization
    ├── wechat_api_utils.py     # WeChat API utility class
    ├── get_access_token.yaml   # Get access token tool configuration
    ├── get_access_token.py     # Get access token tool implementation
    ├── upload_material.yaml   # Upload material tool configuration
    ├── upload_material.py     # Upload material tool implementation
    ├── get_material.yaml      # Get material tool configuration
    ├── get_material.py        # Get material tool implementation
    ├── delete_material.yaml   # Delete material tool configuration
    ├── delete_material.py     # Delete material tool implementation
    ├── create_draft.yaml      # Create draft tool configuration
    ├── create_draft.py        # Create draft tool implementation
    ├── publish_draft.yaml     # Publish draft tool configuration
    └── publish_draft.py       # Publish draft tool implementation
```

## Technical Specifications

- **Python Version**: 3.12+
- **Architecture Support**: AMD64, ARM64
- **Memory Requirements**: 1MB
- **Dependencies**: 
  - `dify_plugin`: Dify plugin development framework
  - `python-dotenv>=1.0.0`: Environment variable management
  - `Pillow>=10.0.0`: Image processing support

## Quick Start

### 1. Environment Setup

Ensure your system has Python 3.12 or higher installed.

### 2. Install Dependencies

```bash
cd wechat_official_plugin
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the environment variable example file and configure your WeChat Official Account information:

```bash
cp .env.example .env
```

Edit the `.env` file and fill in your WeChat Official Account configuration:

```env
# WeChat Official Account Configuration
WECHAT_APP_ID=your_app_id_here
WECHAT_APP_SECRET=your_app_secret_here
```

### 4. Run Plugin

```bash
python main.py
```

## Plugin Installation

### Custom Plugin Local Upload

If you encounter an exception message during plugin installation:
```
plugin verification has been enabled, and the plugin you want to install has a bad signature
```

**Solution (Simple and Direct)**:

Directly modify Dify's `.env` file:
```env
FORCE_VERIFYING_SIGNATURE=false
```

**Note**: After adding this, you need to restart Docker by executing the following commands in the command line:
```bash
cd docker  # First switch to the docker directory under your local Dify installation directory
docker compose down
docker compose up -d
```

## Configuration Guide

### WeChat Official Account Configuration

Before using the plugin, you need to obtain the following information from WeChat Official Account Platform:

1. **App ID**: WeChat Official Account application ID
2. **App Secret**: WeChat Official Account application secret

### Steps to Get Configuration Information

1. Login to [WeChat Official Account Platform](https://mp.weixin.qq.com/)
2. Go to "Development" -> "Basic Configuration"
3. Get "Developer ID (AppID)" and "Developer Password (AppSecret)"
4. Ensure the official account is verified and has relevant interface permissions enabled

### FILES_URL Configuration

Used to display file preview or download links to the frontend, or as multimodal input; links are signed and have expiration times.

**File processing plugins must configure FILES_URL**:
- If the address is `https://example.com`, set `FILES_URL=https://example.com`
- If the address is `http://example.com`, set `FILES_URL=http://example.com`

**Modify Dify's `.env` file**:
```env
FILES_URL=http://<your_IP_address>
```

**Restart Docker service**:
```bash
docker compose down
docker compose up -d
```

## Tool Usage Guide

### Get Access Token

```python
# Get access token
result = get_access_token_tool.invoke({
    # No additional parameters needed, uses configured App ID and App Secret
})
```

### Upload Materials

```python
# Upload image material
result = upload_material_tool.invoke({
    "media_type": "image",
    "file_url": "https://example.com/image.jpg"
})

# Upload video material
result = upload_material_tool.invoke({
    "media_type": "video",
    "file_url": "https://example.com/video.mp4",
    "title": "Video Title",
    "introduction": "Video Description"
})

# Upload audio material
result = upload_material_tool.invoke({
    "media_type": "voice",
    "file_url": "https://example.com/audio.mp3"
})
```

### Get and Delete Materials

```python
# Get material information
result = get_material_tool.invoke({
    "media_id": "your_media_id"
})

# Delete material
result = delete_material_tool.invoke({
    "media_id": "your_media_id"
})
```

### Create and Publish Drafts

```python
# Create article draft
result = create_draft_tool.invoke({
    "title": "Article Title",
    "content": "<p>Article Content HTML</p>",
    "author": "Author Name",
    "digest": "Article Summary",
    "thumb_media_id": "cover_image_media_id",
    "content_source_url": "https://example.com",
    "need_open_comment": "1",
    "only_fans_can_comment": "0"
})

# Publish draft
result = publish_draft_tool.invoke({
    "media_id": "draft_media_id"
})
```

## Error Handling

The plugin includes comprehensive error handling mechanisms, including:

- **Network Errors**: Automatic retry and timeout handling (30-second timeout)
- **API Errors**: Detailed error code explanations and handling suggestions
- **Parameter Validation**: Input parameter format and validity checks
- **File Processing**: File size, format, and permission checks
- **Encoding Processing**: Perfect support for Chinese character encoding and display
- **Credential Management**: Automatic validation and refresh of access tokens

## Featured Capabilities

### 🌟 Perfect Chinese Character Support
The plugin has completely resolved Chinese character encoding issues:
- ✅ Perfect support for Chinese in draft titles, content, authors, and other fields
- ✅ Correct handling of Unicode characters during JSON data transmission
- ✅ Proper display of Chinese content in WeChat API responses
- ✅ No manual handling of Unicode escape sequences required

### 🛡️ Smart Parameter Validation
- Title length limit (≤64 characters)
- Author name length limit (≤8 characters)
- Summary length limit (≤120 characters)
- Cover image media_id format validation
- HTML content security checks

## Important Notes

1. **Interface Permissions**: Ensure your WeChat Official Account has the relevant interface permissions enabled
2. **Call Frequency**: Comply with WeChat API call frequency limits
3. **File Size**: Different material types have different file size limits
4. **Content Review**: Published content needs to pass WeChat platform review
5. **Original Protection**: If there are original declarations, they need to pass original review
6. **Character Encoding**: The plugin automatically handles Chinese character encoding, no additional configuration needed

## Troubleshooting

### "Invalid credentials" Error 🔥 **Most Common Issue**

If you encounter an "Invalid credentials" error when configuring the plugin, please follow these troubleshooting steps:

#### Quick Diagnosis
```bash
# Use built-in diagnostic tool
python diagnostic.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET
```

#### Manual Check Steps

1. **Verify Credential Format**
   - App ID: Must start with `wx`, total length 18 characters
   - App Secret: Must be a 32-character hexadecimal string
   - Ensure no extra spaces or line breaks

2. **Confirm Credential Source**
   - Login to [WeChat Official Account Platform](https://mp.weixin.qq.com/)
   - Go to "Development" -> "Basic Configuration"
   - Copy the correct "Developer ID (AppID)" and "Developer Password (AppSecret)"

3. **Check Official Account Status**
   - ✅ Official account is verified
   - ✅ Material management interface permissions are enabled
   - ✅ Draft box/publishing interface permissions are enabled

4. **Network Connection Test**
   ```bash
   # Test if WeChat API is accessible
   curl -I https://api.weixin.qq.com
   ```

#### Common Error Code Explanations

| Error Code | Description | Solution |
|------------|-------------|----------|
| 40013 | Invalid AppID | Check App ID format and validity |
| 41004 | Missing secret parameter | Confirm App Secret is correctly filled |
| 42001 | access_token timeout | Re-obtain access token |
| 48001 | API function not authorized | Confirm official account has relevant interface permissions enabled |

**Detailed Troubleshooting Guide**: Please refer to [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md)

## Technical Support

If you encounter problems during use, please check:

1. WeChat Official Account configuration is correct
2. Network connection is normal
3. API permissions are enabled
4. Call parameters meet requirements

### Getting Help

1. **Run Diagnostic Tool**: `python diagnostic.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET`
2. **Check Detailed Logs**: Check error information in Dify system logs
3. **Reference Documentation**: See [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) for detailed solutions

## Changelog

### v0.0.1 (2025-09-05)
- 🎉 Initial version release
- ✅ Support for access token acquisition and management
- ✅ Support for permanent material upload, retrieval, and deletion
- ✅ Support for article draft creation and publishing
- ✅ Complete error handling and parameter validation mechanisms
- ✅ Fixed Chinese character encoding issues, perfect Unicode support
- ✅ Smart file processing and format validation
- ✅ 30-second timeout setting adapted to WeChat API response times
- ✅ Detailed error diagnosis and user-friendly error prompts

## License

This project is licensed under the MIT License. See the LICENSE file for details.