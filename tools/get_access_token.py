from typing import Any, Dict
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from .wechat_api_utils import WeChatRequest


class GetAccessTokenTool(Tool):
    """
    获取微信公众号访问令牌工具
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用获取访问令牌工具
        
        Args:
            tool_parameters: 工具参数，包含force_refresh
            
        Yields:
            ToolInvokeMessage: 工具调用消息
        """
        try:
            # 获取凭据
            app_id = self.runtime.credentials.get('app_id')
            app_secret = self.runtime.credentials.get('app_secret')
            
            if not app_id or not app_secret:
                raise ToolProviderCredentialValidationError('App ID和App Secret不能为空')
            
            # 获取参数
            force_refresh = tool_parameters.get('force_refresh', False)
            
            # 创建微信API客户端
            client = WeChatRequest(app_id, app_secret)
            
            # 获取访问令牌
            access_token = client.get_access_token(force_refresh)
            
            yield self.create_text_message(access_token)
            
        except Exception as e:
            yield self.create_text_message(f'获取访问令牌时发生错误: {str(e)}')