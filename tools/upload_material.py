import urllib.request
import json
from typing import Any, Dict, Union
from collections.abc import Generator
from io import BytesIO
from PIL import Image
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .wechat_api_utils import WeChatRequest


class UploadMaterialTool(Tool):
    """
    上传永久素材工具
    """
    
    def _parse_file_input(self, file_input: Union[str, dict]) -> tuple[str, str]:
        """
        解析文件输入，支持Dify格式和普通URL
        
        Args:
            file_input: 文件输入，可以是字符串URL或Dify格式的字典
            
        Returns:
            tuple: (file_url, detected_media_type)
        """
        if isinstance(file_input, str):
            try:
                # 尝试解析为JSON（Dify格式）
                file_data = json.loads(file_input)
                if isinstance(file_data, dict):
                    file_url = file_data.get('file_url', '')
                    media_type = file_data.get('media_type', '')
                    return file_url, media_type
            except (json.JSONDecodeError, ValueError):
                # 如果不是JSON，当作普通URL处理
                pass
            
            # 普通URL字符串
            return file_input, ''
        
        elif isinstance(file_input, dict):
            # 直接是字典格式（Dify格式）
            file_url = file_input.get('file_url', '')
            media_type = file_input.get('media_type', '')
            return file_url, media_type
        
        else:
            # 其他类型，返回空值
            return '', ''
    
    def _download_file(self, file_url: str) -> tuple[bytes, str]:
        """
        下载文件并返回文件数据和文件名
        
        Args:
            file_url: 文件URL
            
        Returns:
            tuple: (file_data, filename)
        """
        try:
            # 创建请求，添加User-Agent头
            req = urllib.request.Request(
                file_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f'HTTP状态码: {response.status}')
                
                # 获取文件名
                filename = self._extract_filename(response, file_url)
                
                # 读取文件数据
                file_data = response.read()
                
                if not file_data:
                    raise Exception('文件内容为空')
                
                return file_data, filename
                
        except urllib.error.URLError as e:
            raise Exception(f'网络错误: {str(e)}')
        except Exception as e:
            raise Exception(f'下载失败: {str(e)}')
    
    def _validate_and_process_image(self, file_data: bytes, filename: str) -> tuple[bytes, str]:
        """
        验证和处理图片文件，参考nano项目的图片处理逻辑
        
        Args:
            file_data: 原始文件数据
            filename: 文件名
            
        Returns:
            tuple: (processed_file_data, processed_filename)
        """
        try:
            # 验证图像数据
            image = Image.open(BytesIO(file_data))
            
            # 获取图片信息
            width, height = image.size
            format_name = image.format or 'UNKNOWN'
            
            # 检查图片尺寸（微信要求）
            if width > 2048 or height > 2048:
                # 按比例缩放到2048以内
                max_size = 2048
                if width > height:
                    new_width = max_size
                    new_height = int(height * max_size / width)
                else:
                    new_height = max_size
                    new_width = int(width * max_size / height)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = new_width, new_height
            
            # 转换为支持的格式（PNG或JPEG）
            img_byte_arr = BytesIO()
            
            # 如果是透明图片，保存为PNG；否则保存为JPEG以减小文件大小
            if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                image.save(img_byte_arr, format='PNG', optimize=True)
                processed_filename = filename.rsplit('.', 1)[0] + '.png'
            else:
                # 转换为RGB模式（JPEG不支持透明度）
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
                processed_filename = filename.rsplit('.', 1)[0] + '.jpg'
            
            processed_data = img_byte_arr.getvalue()
            
            return processed_data, processed_filename
            
        except Exception as e:
            raise Exception(f'图片处理失败: {str(e)}')
    
    def _validate_media_file(self, file_data: bytes, media_type: str, filename: str) -> tuple[bytes, str]:
        """
        根据媒体类型验证和处理文件
        
        Args:
            file_data: 文件数据
            media_type: 媒体类型
            filename: 文件名
            
        Returns:
            tuple: (processed_file_data, processed_filename)
        """
        if media_type in ['image', 'thumb']:
            return self._validate_and_process_image(file_data, filename)
        else:
            # 对于非图片文件，直接返回原数据
            return file_data, filename
    
    def _extract_filename(self, response, file_url: str) -> str:
        """
        从响应头或URL中提取文件名
        
        Args:
            response: HTTP响应对象
            file_url: 文件URL
            
        Returns:
            str: 文件名
        """
        # 尝试从Content-Disposition头获取文件名
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            try:
                filename = content_disposition.split('filename=')[1].strip('"\'')
                if filename:
                    return filename
            except:
                pass
        
        # 从URL中提取文件名
        try:
            from urllib.parse import urlparse, unquote
            parsed_url = urlparse(file_url)
            filename = unquote(parsed_url.path.split('/')[-1])
            if filename and '.' in filename:
                return filename
        except:
            pass
        
        # 默认文件名
        return 'uploaded_file'
    
    def _get_max_file_size(self, media_type: str) -> int:
        """
        获取不同媒体类型的最大文件大小限制（字节）
        
        Args:
            media_type: 媒体类型
            
        Returns:
            int: 最大文件大小（字节）
        """
        size_limits = {
            'image': 10 * 1024 * 1024,    # 10MB
            'voice': 2 * 1024 * 1024,     # 2MB
            'video': 20 * 1024 * 1024,    # 20MB
            'thumb': 64 * 1024            # 64KB
        }
        return size_limits.get(media_type, 10 * 1024 * 1024)  # 默认10MB
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用上传永久素材API
        
        Args:
            tool_parameters: 工具参数
            
        Returns:
            ToolInvokeMessage: 包含上传结果的消息
        """
        try:
            # 获取凭据
            app_id = self.runtime.credentials.get('app_id')
            app_secret = self.runtime.credentials.get('app_secret')
            
            if not app_id or not app_secret:
                yield self.create_text_message('❌ 错误：缺少App ID或App Secret配置')
                yield self.create_text_message('💡 请在插件配置中设置微信公众号的App ID和App Secret')
                return
            
            # 获取参数
            media_type = tool_parameters.get('media_type')
            file_input = tool_parameters.get('file_url')
            title = tool_parameters.get('title', '')
            introduction = tool_parameters.get('introduction', '')
            
            if not media_type or not file_input:
                yield self.create_text_message('❌ 错误：缺少必要参数（媒体类型或文件URL）')
                return
            
            # 解析文件URL（支持Dify格式和普通URL）
            file_url, detected_media_type = self._parse_file_input(file_input)
            
            # 验证媒体类型
            valid_types = ['image', 'voice', 'video', 'thumb']
            if media_type not in valid_types:
                yield self.create_text_message(
                    f'❌ 错误：不支持的媒体类型 {media_type}'
                )
                yield self.create_text_message(f'💡 支持的类型：{"、".join(valid_types)}')
                return
            
            # 下载文件
            try:
                file_data, filename = self._download_file(file_url)
                
                # 验证文件大小
                file_size = len(file_data)
                max_size = self._get_max_file_size(media_type)
                if file_size > max_size:
                    yield self.create_text_message(
                        f'❌ 文件过大：{self._format_file_size(file_size)}'
                    )
                    yield self.create_text_message(
                        f'💡 {media_type}类型的最大限制：{self._format_file_size(max_size)}'
                    )
                    return
                    
            except Exception as e:
                yield self.create_text_message(f'❌ 下载文件失败: {str(e)}')
                yield self.create_text_message('💡 请检查文件URL是否有效，或网络连接是否正常')
                return
            
            # 处理和验证文件
            if media_type in ['image', 'thumb']:
                try:
                    processed_data, processed_filename = self._validate_media_file(file_data, media_type, filename)
                    file_data = processed_data
                    filename = processed_filename
                        
                except Exception as e:
                    yield self.create_text_message(f'❌ 图片处理失败: {str(e)}')
                    yield self.create_text_message('💡 请确保上传的是有效的图片文件')
                    return
            
            # 创建微信API客户端并上传素材
            client = WeChatRequest(app_id, app_secret)
            result = client.upload_material(media_type, file_data, filename, title, introduction)
            
            # 成功上传
            if result.get('errcode') == 0 or 'media_id' in result:
                media_id = result.get('media_id')
                yield self.create_text_message(media_id)
            else:
                error_code = result.get('errcode', -1)
                error_msg = self._get_error_message(error_code)
                yield self.create_text_message(f'❌ 上传失败：{error_msg} (错误码: {error_code})')
                
                # 提供针对性的解决建议
                if error_code == 40113:
                    yield self.create_text_message('💡 解决建议：')
                    yield self.create_text_message('1. 检查文件格式是否为微信支持的格式')
                    yield self.create_text_message('2. 确保图片格式为JPG、PNG等常见格式')
                    yield self.create_text_message('3. 检查文件是否损坏')
                elif error_code in [40001, 40013]:
                    yield self.create_text_message('💡 请检查App ID和App Secret配置是否正确')
                elif error_code == 45001:
                    yield self.create_text_message('💡 请检查文件大小是否超出限制')
                
        except Exception as e:
            yield self.create_text_message(f'❌ 上传素材时发生未知错误: {str(e)}')
            yield self.create_text_message('🔧 请联系技术支持或查看详细日志')
    
    def _get_file_extension(self, file_url: str, media_type: str) -> str:
        """
        根据文件URL和媒体类型获取文件扩展名
        
        Args:
            file_url: 文件URL
            media_type: 媒体类型
            
        Returns:
            str: 文件扩展名
        """
        # 从URL中提取扩展名
        if '.' in file_url:
            extension = file_url.split('.')[-1].split('?')[0].lower()
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'mp3', 'wma', 'wav', 'amr', 'mp4', 'avi']:
                return extension
        
        # 根据媒体类型返回默认扩展名
        default_extensions = {
            'image': 'jpg',
            'voice': 'mp3',
            'video': 'mp4',
            'thumb': 'jpg'
        }
        
        return default_extensions.get(media_type, 'bin')
    
    def _get_content_type(self, media_type: str) -> str:
        """
        根据媒体类型获取Content-Type
        
        Args:
            media_type: 媒体类型
            
        Returns:
            str: Content-Type
        """
        content_types = {
            'image': 'image/jpeg',
            'voice': 'audio/mpeg',
            'video': 'video/mp4',
            'thumb': 'image/jpeg'
        }
        
        return content_types.get(media_type, 'application/octet-stream')
    
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
            40004: '不合法的媒体文件类型',
            40005: '不合法的文件类型',
            40006: '不合法的文件大小',
            40007: '不合法的媒体文件id',
            41001: '缺少access_token参数',
            42001: 'access_token超时',
            43002: '需要POST请求',
            44001: '多媒体文件为空',
            45001: '多媒体文件大小超过限制',
            40113: '不支持的媒体文件格式',
            45002: '消息内容超过限制',
            45003: '标题字段超过限制',
            45004: '描述字段超过限制',
            48001: 'api功能未授权',
            48004: 'api禁止删除被自动回复和自定义菜单引用的素材',
            50001: '用户未授权该api',
            50002: '用户受限，可能是违规后接口被封禁'
        }
        
        return error_messages.get(errcode, f'未知错误码: {errcode}')