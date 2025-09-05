import urllib.request
import json
from typing import Any, Dict, Union
from collections.abc import Generator
from io import BytesIO
from PIL import Image
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .wechat_api_utils import WeChatRequest


class UploadImageTool(Tool):
    """
    上传图文消息图片工具
    """
    
    def _parse_file_input(self, file_input: Union[str, dict]) -> str:
        """
        解析文件输入，支持Dify格式和普通URL
        
        Args:
            file_input: 文件输入，可以是字符串URL或Dify格式的字典
            
        Returns:
            str: 文件URL
        """
        if isinstance(file_input, str):
            try:
                # 尝试解析为JSON（Dify格式）
                file_data = json.loads(file_input)
                if isinstance(file_data, dict):
                    return file_data.get('file_url', '')
            except (json.JSONDecodeError, ValueError):
                # 如果不是JSON，当作普通URL处理
                pass
            
            # 普通URL字符串
            return file_input
        
        elif isinstance(file_input, dict):
            # 直接是字典格式（Dify格式）
            return file_input.get('file_url', '')
        
        else:
            # 其他类型，返回空值
            return ''
    
    def _download_file(self, file_url: str) -> tuple[bytes, str]:
        """
        下载文件
        
        Args:
            file_url: 文件URL
            
        Returns:
            tuple: (文件数据, 文件名)
        """
        try:
            request = urllib.request.Request(file_url)
            request.add_header('User-Agent', 'Mozilla/5.0 (compatible; DifyBot/1.0)')
            
            with urllib.request.urlopen(request, timeout=30) as response:
                file_data = response.read()
                filename = self._extract_filename(response, file_url)
                
                return file_data, filename
                
        except Exception as e:
            raise Exception(f'下载文件失败: {str(e)}')
    
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
            except (IndexError, AttributeError):
                pass
        
        # 从URL中提取文件名
        try:
            filename = file_url.split('/')[-1].split('?')[0]
            if filename and '.' in filename:
                return filename
        except (IndexError, AttributeError):
            pass
        
        # 默认文件名
        return 'image.jpg'
    
    def _validate_image(self, file_data: bytes, filename: str) -> tuple[bytes, str]:
        """
        验证和处理图片文件
        
        Args:
            file_data: 文件数据
            filename: 文件名
            
        Returns:
            tuple: (处理后的文件数据, 最终文件名)
        """
        try:
            # 使用PIL验证图片
            image = Image.open(BytesIO(file_data))
            
            # 检查图片格式
            if image.format not in ['JPEG', 'PNG']:
                # 转换为JPEG格式
                if image.mode in ('RGBA', 'LA', 'P'):
                    # 处理透明通道
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 保存为JPEG
                output = BytesIO()
                image.save(output, format='JPEG', quality=85, optimize=True)
                file_data = output.getvalue()
                filename = filename.rsplit('.', 1)[0] + '.jpg'
            
            return file_data, filename
            
        except Exception as e:
            raise Exception(f'图片验证失败: {str(e)}')
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小显示
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化的文件大小
        """
        if size_bytes < 1024:
            return f'{size_bytes} B'
        elif size_bytes < 1024 * 1024:
            return f'{size_bytes / 1024:.1f} KB'
        else:
            return f'{size_bytes / (1024 * 1024):.1f} MB'
    

    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用上传图文消息图片API
        
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
            image_input = tool_parameters.get('image_url')
            
            if not image_input:
                yield self.create_text_message('❌ 错误：缺少图片URL参数')
                return
            
            # 解析图片URL（支持Dify格式和普通URL）
            image_url = self._parse_file_input(image_input)
            
            if not image_url:
                yield self.create_text_message('❌ 错误：无效的图片URL')
                return
            
            yield self.create_text_message('🔄 开始下载图片...')
            
            # 下载图片
            try:
                file_data, filename = self._download_file(image_url)
                
                # 验证文件大小（1MB限制）
                file_size = len(file_data)
                max_size = 1024 * 1024  # 1MB
                if file_size > max_size:
                    yield self.create_text_message(
                        f'❌ 图片过大：{self._format_file_size(file_size)}'
                    )
                    yield self.create_text_message(
                        f'💡 图文消息图片的最大限制：{self._format_file_size(max_size)}'
                    )
                    return
                    
            except Exception as e:
                yield self.create_text_message(f'❌ 下载图片失败: {str(e)}')
                yield self.create_text_message('💡 请检查图片URL是否有效，或网络连接是否正常')
                return
            
            yield self.create_text_message('🔄 验证图片格式...')
            
            # 验证和处理图片
            try:
                file_data, filename = self._validate_image(file_data, filename)
            except Exception as e:
                yield self.create_text_message(f'❌ 图片验证失败: {str(e)}')
                yield self.create_text_message('💡 请确保上传的是有效的JPG或PNG图片文件')
                return
            
            yield self.create_text_message('🔄 上传图片到微信服务器...')
            
            # 创建微信API请求
            wechat_request = WeChatRequest(app_id, app_secret)
            
            try:
                # 调用上传图片API
                result = wechat_request.upload_image(file_data, filename)
                
                if result.get('errcode', 0) == 0:
                    # 上传成功
                    image_url = result.get('url', '')
                    
                    yield self.create_text_message(image_url)
                    
                else:
                    # 上传失败
                    errcode = result.get('errcode', 0)
                    errmsg = result.get('errmsg', '未知错误')
                    error_desc = wechat_request._get_error_message(errcode)
                    
                    yield self.create_text_message(f'❌ 上传失败 (错误码: {errcode})')
                    yield self.create_text_message(f'📝 错误信息: {errmsg}')
                    yield self.create_text_message(f'💡 解决方案: {error_desc}')
                    
            except Exception as e:
                yield self.create_text_message(f'❌ API调用失败: {str(e)}')
                yield self.create_text_message('💡 请检查网络连接或稍后重试')
                return
                
        except Exception as e:
            yield self.create_text_message(f'❌ 工具执行失败: {str(e)}')
            yield self.create_text_message('💡 请检查参数配置或联系技术支持')
            return