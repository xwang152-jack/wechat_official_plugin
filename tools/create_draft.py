import json
from typing import Any, Dict, Union
from collections.abc import Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .wechat_api_utils import WeChatRequest


class CreateDraftTool(Tool):
    """
    创建图文消息草稿工具
    """
    

    
    def _invoke(
        self, tool_parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        调用创建草稿工具
        
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
            title = tool_parameters.get('title', '')
            content = tool_parameters.get('content', '')
            author = tool_parameters.get('author', '')
            digest = tool_parameters.get('digest', '')
            thumb_media_id = tool_parameters.get('thumb_media_id', '')
            content_source_url = tool_parameters.get('content_source_url', '')
            need_open_comment = int(tool_parameters.get('need_open_comment', '0'))
            only_fans_can_comment = int(tool_parameters.get('only_fans_can_comment', '0'))
            
            if not title:
                yield self.create_text_message('错误：缺少文章标题')
                return
                
            if not content:
                yield self.create_text_message('错误：缺少文章内容')
                return
            
            # 创建微信API客户端
            client = WeChatRequest(app_id, app_secret)
            
            # 检查是否提供了封面图片（对于图文消息是必需的）
            if not thumb_media_id:
                yield self.create_text_message('错误：创建草稿需要提供封面图片的media_id，请先上传图片素材')
                return
            
            # 参数验证和诊断
            validation_errors = []
            
            # 检查字段长度限制
            if len(title) > 64:
                validation_errors.append(f"📏 标题过长：{len(title)}/64字符，请缩短标题")
            
            if author and len(author) > 8:
                validation_errors.append(f"👤 作者名过长：{len(author)}/8字符，请缩短作者名")
            
            if digest and len(digest) > 120:
                validation_errors.append(f"📝 摘要过长：{len(digest)}/120字符，请缩短摘要")
            
            # 检查media_id格式
            if not thumb_media_id.strip():
                validation_errors.append("🖼️ 封面图片media_id为空")
            elif len(thumb_media_id) < 10:
                validation_errors.append("🖼️ 封面图片media_id格式可能不正确，长度过短")
            
            # 检查内容中的潜在问题
            if '<script' in content.lower() or '<iframe' in content.lower():
                validation_errors.append("⚠️ 内容包含可能不被允许的HTML标签（script/iframe）")
            
            if validation_errors:
                error_msg = "❌ 参数验证失败：\n\n" + "\n".join(validation_errors)
                error_msg += "\n\n💡 请修正以上问题后重试"
                yield self.create_text_message(error_msg)
                return
            
            # 构建文章数据（符合微信API规范）
            article_data = {
                "article_type": "news",  # 默认为图文消息
                "title": title,
                "content": content,
                "author": author,
                "digest": digest,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": need_open_comment,
                "only_fans_can_comment": only_fans_can_comment
            }
            
            # 如果提供了原文链接，添加到文章数据中
            if content_source_url:
                article_data["content_source_url"] = content_source_url
            
            # 构建文章列表（微信API要求是数组格式）
            articles_json = json.dumps([article_data], ensure_ascii=False)
            
            # 创建草稿
            result = client.create_draft(articles_json)
            
            # 成功创建
            display_title = str(title)
            display_author = str(author) if author else '未设置'
            display_digest = str(digest) if digest else '未设置'
            
            success_message = (
                f"✅ 草稿创建成功\n"
                f"📄 标题: {display_title}\n"
                f"🆔 草稿ID: {result['media_id']}\n"
                f"👤 作者: {display_author}\n"
                f"📝 摘要: {display_digest}\n"
                f"📊 状态: 草稿已保存，可进行发布"
            )
            
            yield self.create_text_message(success_message)
                
        except Exception as e:
            error_msg = str(e)
            
            # 提供更详细的错误诊断信息
            if '45110' in error_msg:
                detailed_msg = (
                    f"❌ 创建草稿失败 (错误码: 45110)\n\n"
                    f"🔍 可能的原因：\n"
                    f"1. 📝 文章内容格式不符合微信规范\n"
                    f"2. 🖼️ 封面图片media_id无效或已过期\n"
                    f"3. 📏 标题、摘要或作者字段超出长度限制\n"
                    f"4. 🔑 公众号权限不足，未开通草稿功能\n"
                    f"5. 🌐 内容包含违规信息或敏感词汇\n\n"
                    f"💡 解决建议：\n"
                    f"• 检查封面图片是否已成功上传并获得有效media_id\n"
                    f"• 确认标题≤64字符，摘要≤120字符，作者≤8字符\n"
                    f"• 验证文章内容是否包含HTML标签或特殊字符\n"
                    f"• 确保公众号已认证并开通相关接口权限\n"
                    f"• 检查内容是否符合微信内容规范"
                )
                yield self.create_text_message(detailed_msg)
            elif '40164' in error_msg:
                yield self.create_text_message(
                    f"❌ IP地址不在白名单中\n\n"
                    f"请在微信公众平台后台添加服务器IP到白名单：\n"
                    f"1. 登录微信公众平台 (mp.weixin.qq.com)\n"
                    f"2. 进入开发 -> 基本配置\n"
                    f"3. 在IP白名单中添加当前服务器IP地址"
                )
            elif '42001' in error_msg:
                yield self.create_text_message(
                    f"❌ access_token已过期\n\n"
                    f"请重新获取access_token或检查AppID和AppSecret配置"
                )
            elif '48001' in error_msg:
                yield self.create_text_message(
                    f"❌ 接口权限不足\n\n"
                    f"请确认公众号已获得草稿管理接口权限，\n"
                    f"可在公众平台官网-开发者中心查看接口权限"
                )
            else:
                yield self.create_text_message(f'创建草稿时发生错误: {error_msg}')
    
    def _validate_article(self, article: Dict[str, Any], index: int) -> Union[Dict[str, Any], str]:
        """
        验证文章数据
        
        Args:
            article: 文章数据
            index: 文章索引
            
        Returns:
            Union[Dict[str, Any], str]: 验证后的文章数据或错误信息
        """
        required_fields = ['title', 'content', 'thumb_media_id']
        
        # 检查必需字段
        for field in required_fields:
            if field not in article or not article[field]:
                return f'第{index}篇文章缺少必需字段: {field}'
        
        # 验证字段长度
        if len(article['title']) > 64:
            return f'第{index}篇文章标题超过64个字符限制'
        
        if len(article.get('digest', '')) > 120:
            return f'第{index}篇文章摘要超过120个字符限制'
        
        if len(article.get('author', '')) > 8:
            return f'第{index}篇文章作者名称超过8个字符限制'
        
        # 构建标准文章结构
        validated_article = {
            'title': article['title'],
            'author': article.get('author', ''),
            'digest': article.get('digest', ''),
            'content': article['content'],
            'content_source_url': article.get('content_source_url', ''),
            'thumb_media_id': article['thumb_media_id'],
            'show_cover_pic': int(article.get('show_cover_pic', 0)),
            'need_open_comment': int(article.get('need_open_comment', 0)),
            'only_fans_can_comment': int(article.get('only_fans_can_comment', 0))
        }
        
        return validated_article
    
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
            44003: '图文消息内容为空',
            45001: '多媒体文件大小超过限制',
            45002: '消息内容超过限制',
            45003: '标题字段超过限制',
            45004: '描述字段超过限制',
            45005: '链接字段超过限制',
            45008: '图文消息超过限制',
            45110: '草稿创建失败，可能是参数格式错误或权限不足（常见原因：作者名超过8字符、标题超过64字符、摘要超过120字符）',
            47001: '解析JSON/XML内容错误',
            48001: 'api功能未授权',
            50001: '用户未授权该api',
            50002: '用户受限，可能是违规后接口被封禁',
            85023: '草稿箱已满，请删除部分草稿后重试',
            85024: '草稿不存在',
            85025: '草稿已发布，不能重复发布'
        }
        
        return error_messages.get(errcode, f'未知错误码: {errcode}')