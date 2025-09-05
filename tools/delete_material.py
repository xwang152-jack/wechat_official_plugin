from typing import Any, Dict
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .wechat_api_utils import WeChatRequest


class DeleteMaterialTool(Tool):
    """
    删除永久素材工具
    """
    
    def _invoke(
        self, tool_parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用删除永久素材工具
        
        Args:
            tool_parameters: 工具参数
            
        Yields:
            ToolInvokeMessage: 工具调用消息
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
            
            # 删除素材
            result = client.delete_material(media_id)
            
            # 成功删除
            success_message = (
                f"✅ 素材删除成功\n"
                f"🆔 已删除媒体ID: {media_id}"
            )
            
            yield self.create_text_message(success_message)
                
        except Exception as e:
            yield self.create_text_message(f'删除素材时发生错误: {str(e)}')