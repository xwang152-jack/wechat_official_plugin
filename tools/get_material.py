import re
from typing import Any, Dict
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .wechat_api_utils import WeChatRequest


class GetMaterialTool(Tool):
    """
    获取永久素材工具
    """
    
    def _decode_unicode_escapes(self, text: str) -> str:
        """
        解码Unicode转义序列
        
        Args:
            text: 可能包含Unicode转义序列的文本
            
        Returns:
            str: 解码后的文本
        """
        if not isinstance(text, str):
            return str(text)
        
        # 查找所有Unicode转义序列
        def replace_unicode(match):
            unicode_str = match.group(0)
            try:
                # 将\uXXXX转换为对应的Unicode字符
                return unicode_str.encode().decode('unicode_escape')
            except:
                return unicode_str
        
        # 使用正则表达式查找并替换Unicode转义序列
        pattern = r'\\u[0-9a-fA-F]{4}'
        return re.sub(pattern, replace_unicode, text)
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用获取永久素材API
        
        Args:
            tool_parameters: 工具参数
            
        Returns:
            ToolInvokeMessage: 包含素材信息的消息
        """
        try:
            # 获取凭据
            app_id = self.runtime.credentials.get('app_id')
            app_secret = self.runtime.credentials.get('app_secret')
            
            if not app_id or not app_secret:
                yield self.create_text_message('错误：缺少App ID或App Secret配置')
                return
            
            # 获取参数
            media_id = tool_parameters.get('media_id')
            
            if not media_id:
                yield self.create_text_message('错误：缺少媒体ID')
                return
            
            # 创建微信API客户端
            client = WeChatRequest(app_id, app_secret)
            
            # 获取素材
            result = client.get_material(media_id)
            
            # 处理图文消息
            if 'news_item' in result:
                message = self._handle_news_material(result)
                yield message
            elif 'binary_data' in result:
                # 处理二进制素材（图片、音频、视频等）
                message = self._handle_binary_material_data(
                    result['binary_data'], 
                    result['headers'], 
                    media_id
                )
                yield message
            else:
                # 其他类型素材
                message = (
                    f"✅ 成功获取素材\n"
                    f"🆔 媒体ID: {media_id}\n"
                    f"📄 素材信息已获取"
                )
                
                yield self.create_text_message(message)
                
        except Exception as e:
            yield self.create_text_message(f'获取素材时发生错误: {str(e)}')
    
    def _handle_news_material(self, result: Dict[str, Any]) -> ToolInvokeMessage:
        """
        处理图文素材响应
        
        Args:
            result: API响应结果
            
        Returns:
            ToolInvokeMessage: 包含图文素材信息的消息
        """
        news_items = result.get('news_item', [])
        
        if not news_items:
            return self.create_text_message('图文素材为空')
        
        message_parts = ["📰 图文素材信息：\n"]
        
        for i, item in enumerate(news_items, 1):
            # 解码可能包含Unicode转义序列的文本字段
            title = self._decode_unicode_escapes(item.get('title', '无标题'))
            author = self._decode_unicode_escapes(item.get('author', '无作者'))
            digest = self._decode_unicode_escapes(item.get('digest', '无摘要'))
            content = self._decode_unicode_escapes(item.get('content', '无内容'))
            content_source_url = item.get('content_source_url', '无')
            thumb_media_id = item.get('thumb_media_id', '无')
            show_cover_pic = item.get('show_cover_pic', 0)
            url = item.get('url', '无')
            thumb_url = item.get('thumb_url', '无')
            
            message_parts.append(f"\n📄 第{i}篇文章：")
            message_parts.append(f"📝 标题: {title}")
            message_parts.append(f"✍️ 作者: {author}")
            message_parts.append(f"📋 摘要: {digest[:100]}{'...' if len(digest) > 100 else ''}")
            message_parts.append(f"🔗 原文链接: {content_source_url}")
            message_parts.append(f"🖼️ 封面媒体ID: {thumb_media_id}")
            message_parts.append(f"👁️ 显示封面: {'是' if show_cover_pic else '否'}")
            message_parts.append(f"🌐 文章URL: {url}")
            message_parts.append(f"🖼️ 封面URL: {thumb_url}")
            
            # 内容预览（限制长度）
            if content:
                content_preview = content[:200] + '...' if len(content) > 200 else content
                # 移除HTML标签进行预览
                import re
                content_preview = re.sub(r'<[^>]+>', '', content_preview)
                message_parts.append(f"📖 内容预览: {content_preview}")
        
        return self.create_text_message('\n'.join(message_parts))
    
    def _handle_binary_material_data(self, response_data: bytes, headers: dict, media_id: str) -> ToolInvokeMessage:
        """
        处理二进制素材响应数据
        
        Args:
            response_data: 响应数据
            headers: 响应头
            media_id: 媒体ID
            
        Returns:
            ToolInvokeMessage: 包含素材信息的消息
        """
        content_type = headers.get('Content-Type', '')
        content_length = len(response_data)
        
        # 判断素材类型
        if content_type.startswith('image/'):
            material_type = '🖼️ 图片'
        elif content_type.startswith('audio/'):
            material_type = '🎵 语音'
        elif content_type.startswith('video/'):
            material_type = '🎬 视频'
        else:
            material_type = '📄 文件'
        
        success_message = (
            f"✅ 成功获取素材\n"
            f"📋 媒体ID: {media_id}\n"
            f"📁 类型: {material_type}\n"
            f"📊 大小: {self._format_file_size(content_length)}\n"
            f"🏷️ MIME类型: {content_type}\n"
            f"💾 数据已获取，可用于进一步处理"
        )
        
        return self.create_text_message(success_message)
    
    def _handle_binary_material(self, response, media_id: str) -> ToolInvokeMessage:
        """
        处理二进制素材响应
        
        Args:
            response: HTTP响应对象
            media_id: 媒体ID
            
        Returns:
            ToolInvokeMessage: 包含素材信息的消息
        """
        content_type = response.headers.get('Content-Type', '')
        content_length = len(response.content)
        
        # 判断素材类型
        if content_type.startswith('image/'):
            material_type = '🖼️ 图片'
        elif content_type.startswith('audio/'):
            material_type = '🎵 语音'
        elif content_type.startswith('video/'):
            material_type = '🎬 视频'
        else:
            material_type = '📁 文件'
        
        message = (
            f"✅ 成功获取素材\n"
            f"🆔 媒体ID: {media_id}\n"
            f"📂 素材类型: {material_type}\n"
            f"📏 文件大小: {self._format_file_size(content_length)}\n"
            f"🏷️ Content-Type: {content_type}\n"
            f"\n💡 提示: 这是一个二进制文件，已成功获取到内容。"
        )
        
        return self.create_text_message(message)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _get_error_message(self, errcode: int) -> str:
        """
        根据错误码获取错误信息
        
        Args:
            errcode: 微信API错误码
            
        Returns:
            str: 错误信息
        """
        error_messages = {
            40001: 'access_token无效或已过期',
            40007: '不合法的媒体文件id',
            41001: '缺少access_token参数',
            42001: 'access_token超时',
            43002: '需要POST请求',
            46001: '不存在媒体数据',
            48001: 'api功能未授权',
            50001: '用户未授权该api',
            50002: '用户受限，可能是违规后接口被封禁'
        }
        
        return error_messages.get(errcode, f'未知错误码: {errcode}')