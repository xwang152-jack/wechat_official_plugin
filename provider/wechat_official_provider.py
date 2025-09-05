from typing import Any, Dict
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.wechat_api_utils import auth


class WeChatOfficialProvider(ToolProvider):
    """
    微信公众号工具提供者
    """
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证微信公众号凭据
        
        Args:
            credentials: 包含app_id和app_secret的凭据
            
        Raises:
            ToolProviderCredentialValidationError: 当凭据无效时抛出异常
        """
        auth(credentials)
    
    def _get_error_message(self, errcode: int) -> str:
        """
        根据错误码获取错误信息
        
        Args:
            errcode: 微信API错误码
            
        Returns:
            str: 错误信息
        """
        error_messages = {
            40001: 'AppSecret错误或者AppSecret不属于这个公众号',
            40002: '不合法的凭证类型',
            40004: '不合法的媒体文件类型',
            40005: '不合法的文件类型',
            40006: '不合法的文件大小',
            40007: '不合法的媒体文件id',
            40008: '不合法的消息类型',
            40013: '不合法的AppID',
            40164: '调用接口的IP地址不在白名单中',
            41001: '缺少access_token参数',
            41002: '缺少appid参数',
            41003: '缺少refresh_token参数',
            41004: '缺少secret参数',
            42001: 'access_token超时，请检查access_token的有效期',
            42002: 'refresh_token超时',
            42003: 'oauth_code超时',
            43001: '需要GET请求',
            43002: '需要POST请求',
            43003: '需要HTTPS请求',
            43004: '需要接收者关注',
            43005: '需要好友关系',
            44001: '多媒体文件为空',
            44002: 'POST的数据包为空',
            44003: '图文消息内容为空',
            44004: '文本消息内容为空',
            45001: '多媒体文件大小超过限制',
            45002: '消息内容超过限制',
            45003: '标题字段超过限制',
            45004: '描述字段超过限制',
            45005: '链接字段超过限制',
            45006: '图片链接字段超过限制',
            45007: '语音播放时间超过限制',
            45008: '图文消息超过限制',
            45009: '接口调用超过限制',
            45010: '创建菜单个数超过限制',
            45015: '回复时间超过限制',
            45016: '系统分组，不允许修改',
            45017: '分组名字过长',
            45018: '分组数量超过上限',
            45110: '草稿创建失败，可能是参数格式错误或权限不足',
            46001: '不存在媒体数据',
            46002: '不存在的菜单版本',
            46003: '不存在的菜单数据',
            46004: '不存在的用户',
            47001: '解析JSON/XML内容错误',
            48001: 'api功能未授权，请确认公众号已获得该接口',
            48002: '粉丝拒收消息（粉丝在公众号选项中，关闭了"接收消息"）',
            48003: 'api接口被封禁，请登录mp.weixin.qq.com查看详情',
            48004: 'api禁止删除被自动回复和自定义菜单引用的素材',
            48005: 'api禁止清零调用次数，因为清零次数达到上限',
            48006: '48006 weixin.qq.com域名使用数量超过限制',
            50001: '用户未授权该api',
            50002: '用户受限，可能是违规后接口被封禁',
            61451: '参数错误(invalid parameter)',
            61452: '无效客服账号(invalid kf_account)',
            61453: '客服帐号已存在(kf_account exsited)',
            61454: '客服帐号名长度超过限制(仅允许10个英文字符，不包括@及@后的公众号的微信号)(invalid kf_acount length)',
            61455: '客服帐号名包含非法字符(仅允许英文+数字)(illegal character in kf_account)',
            61456: '客服帐号个数超过限制(10个客服账号)(kf_account count exceeded)',
            61457: '无效头像文件类型(invalid file type)',
            61450: '系统错误(system error)',
            61500: '日期格式错误',
            65301: '不存在此menuid对应的个性化菜单',
            65302: '没有相应的用户',
            65303: '没有默认菜单，不能创建个性化菜单',
            65304: 'MatchRule信息为空',
            65305: '个性化菜单数量受限',
            65306: '不支持个性化菜单的帐号',
            65307: '个性化菜单信息为空',
            65308: '包含没有响应类型的button',
            65309: '个性化菜单开关处于关闭状态',
            65310: '填写了省份或城市信息，国家信息不能为空',
            65311: '填写了城市信息，省份信息不能为空',
            65312: '不合法的国家信息',
            65313: '不合法的省份信息',
            65314: '不合法的城市信息',
            65316: '该公众号的菜单设置了过多的域名外跳（最多跳转到3个域名）',
            65317: '不合法的URL'
        }
        
        return error_messages.get(errcode, f'未知错误码: {errcode}')