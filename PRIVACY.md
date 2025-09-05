# Privacy Policy

This WeChat Official Account plugin integrates with WeChat API services to manage materials, drafts, and content publishing. Here's how your data is handled:

## Data Processing

- **WeChat Credentials**: Your App ID and App Secret are used to authenticate with WeChat Official Account API
- **Access Tokens**: Temporary access tokens are generated and cached for API authentication
- **Media Files**: Images, videos, audio files, and other media content are uploaded to WeChat servers for material management
- **Draft Content**: Article drafts including titles, content, cover images, and metadata are processed and stored on WeChat servers
- **API Communication**: The plugin communicates with WeChat Official Account API (https://api.weixin.qq.com) to perform operations

## Data Storage

- **No Local Storage**: The plugin does not permanently store your WeChat credentials, media files, or draft content locally
- **Temporary Processing**: All data processing is temporary and happens only during API operations
- **Credential Security**: Your App ID and App Secret are stored securely within your environment and are not logged or transmitted elsewhere
- **Token Caching**: Access tokens are temporarily cached in memory for performance optimization and automatically refreshed when expired

## Third-Party Services

- **WeChat Official Account API**: Your content and media files are sent to WeChat servers (https://api.weixin.qq.com) for processing
- **WeChat Platform**: All uploaded materials and published content are stored on WeChat's servers according to their data policies
- **Network Communication**: The plugin requires internet connectivity to communicate with WeChat API servers
- **Service Provider**: WeChat API service processes your requests according to WeChat's privacy policy and terms of service

## Data Operations

### Material Management
- **File Upload**: Media files (images, videos, audio) are uploaded to WeChat servers and assigned unique media IDs
- **File Processing**: Files are validated for format, size limits, and other WeChat requirements before upload
- **Material Retrieval**: Existing materials are fetched from WeChat servers using media IDs
- **Material Deletion**: Materials can be permanently deleted from WeChat servers

### Draft Operations
- **Content Creation**: Article drafts with text content, images, and metadata are created on WeChat servers
- **Draft Publishing**: Draft content is published to your WeChat Official Account and becomes publicly accessible
- **Content Encoding**: All text content is properly encoded to support Chinese characters and special formatting

## Data Retention

- The plugin does not retain any user data after task completion
- Uploaded materials and published content are stored on WeChat servers according to WeChat's retention policies
- Access tokens are automatically discarded when they expire
- No persistent storage of credentials, files, or content within the plugin

## Data Transmission

- All API communications are transmitted securely over HTTPS to WeChat servers
- Media files and content are uploaded securely using WeChat's official API endpoints
- No data is shared with any other third parties beyond the WeChat Official Account service
- All requests include proper authentication and follow WeChat's API security standards

## User Control

- Users have full control over their WeChat Official Account content through the WeChat platform
- Materials and drafts can be managed directly through WeChat Official Account backend
- Users can revoke API access by changing their App Secret in WeChat Official Account settings
- Published content follows WeChat's content management and deletion policies

## Compliance

- This plugin operates within WeChat Official Account API terms of service
- All data processing complies with WeChat's developer policies and guidelines
- Users are responsible for ensuring their content complies with applicable laws and WeChat's content policies
- The plugin does not collect any additional user data beyond what's necessary for WeChat API operations