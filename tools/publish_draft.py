from typing import Any, Dict
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .wechat_api_utils import WeChatRequest


class PublishDraftTool(Tool):
    """
    发布草稿工具
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用发布草稿工具
        
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
                yield self.create_text_message('错误：缺少草稿ID')
                return
            
            # 创建微信API客户端
            client = WeChatRequest(app_id, app_secret)
            
            # 发布草稿
            result = client.publish_draft(media_id)
            
            # 成功发布
            success_message = (
                f"✅ 草稿发布成功\n"
                f"🆔 草稿ID: {media_id}\n"
                f"📰 发布ID: {result['publish_id']}\n"
                f"📊 状态: 文章已发布到公众号\n"
                f"⏰ 发布时间: 即时发布"
            )
            
            yield self.create_text_message(success_message)
                
        except Exception as e:
            yield self.create_text_message(f'发布草稿时发生错误: {str(e)}')
    
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
            44002: 'POST的数据包为空',
            47001: '解析JSON/XML内容错误',
            48001: 'api功能未授权',
            50001: '用户未授权该api',
            50002: '用户受限，可能是违规后接口被封禁',
            85023: '草稿箱已满，请删除部分草稿后重试',
            85024: '草稿不存在',
            85025: '草稿已发布，不能重复发布',
            85026: '原创校验中，请稍后重试',
            85027: '原创校验失败，无法发布',
            85028: '草稿内容涉嫌违规，无法发布',
            85029: '发布任务已存在',
            85030: '发布任务不存在',
            85031: '发布任务状态错误',
            85032: '发布任务已完成',
            85033: '发布任务已取消',
            85034: '发布任务处理中',
            85035: '发布任务失败',
            85036: '草稿已删除，无法发布',
            85037: '文章正在审核中，请稍后重试',
            85038: '文章审核不通过，无法发布',
            85039: '发布频率过快，请稍后重试',
            85040: '今日发布次数已达上限'
        }
        
        return error_messages.get(errcode, f'未知错误码: {errcode}')