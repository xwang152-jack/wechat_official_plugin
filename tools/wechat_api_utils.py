import json
from typing import Any, Optional, Dict
import urllib.request
import urllib.parse
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


def auth(credentials: Dict[str, Any]) -> None:
    """
    验证微信公众号凭据
    
    Args:
        credentials: 包含app_id和app_secret的凭据字典
        
    Raises:
        ToolProviderCredentialValidationError: 当凭据无效时抛出异常
    """
    app_id = credentials.get("app_id")
    app_secret = credentials.get("app_secret")
    if not app_id or not app_secret:
        raise ToolProviderCredentialValidationError("app_id and app_secret is required")
    try:
        client = WeChatRequest(app_id, app_secret)
        assert client.access_token is not None
    except Exception as e:
        raise ToolProviderCredentialValidationError(str(e))


class WeChatRequest:
    """
    微信公众号API请求工具类
    """
    API_BASE_URL = "https://api.weixin.qq.com"
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token = None
    
    @property
    def access_token(self) -> str:
        """
        获取访问令牌，支持缓存
        """
        if not self._access_token:
            self._access_token = self.get_access_token()
        return self._access_token
    
    def _send_request(
        self,
        url: str,
        method: str = "POST",
        require_token: bool = True,
        payload: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        发送HTTP请求的统一方法
        
        Args:
            url: 请求URL
            method: HTTP方法
            require_token: 是否需要访问令牌
            payload: JSON数据
            params: URL参数
            files: 文件数据
            timeout: 超时时间
            
        Returns:
            Dict: API响应数据
            
        Raises:
            Exception: 当API返回错误时抛出异常
        """
        # 构建完整URL
        if params:
            if require_token:
                params['access_token'] = self.access_token
            url_parts = urllib.parse.urlparse(url)
            query = urllib.parse.urlencode(params)
            url = urllib.parse.urlunparse((
                url_parts.scheme, url_parts.netloc, url_parts.path,
                url_parts.params, query, url_parts.fragment
            ))
        elif require_token:
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}access_token={self.access_token}"
        
        # 准备请求数据
        data = None
        headers = {"User-Agent": "Dify WeChat Plugin"}
        
        if files:
            # 处理文件上传
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
            
            body_parts = []
            
            # 添加表单字段
            if payload:
                for key, value in payload.items():
                    body_parts.append(f'--{boundary}'.encode())
                    body_parts.append(f'Content-Disposition: form-data; name="{key}"'.encode())
                    body_parts.append(b'')
                    body_parts.append(str(value).encode())
            
            # 添加文件
            for field_name, file_info in files.items():
                if isinstance(file_info, tuple):
                    file_data, filename = file_info
                else:
                    file_data = file_info
                    filename = 'file'
                
                body_parts.append(f'--{boundary}'.encode())
                body_parts.append(
                    f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode()
                )
                body_parts.append(b'Content-Type: application/octet-stream')
                body_parts.append(b'')
                body_parts.append(file_data)
            
            body_parts.append(f'--{boundary}--'.encode())
            data = b'\r\n'.join(body_parts)
            
        elif payload:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        
        # 发送请求
        req = urllib.request.Request(url, data=data, headers=headers)
        req.get_method = lambda: method.upper()
        
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status != 200:
                    raise Exception(f"HTTP请求失败，状态码: {response.status}")
                
                # 读取响应数据
                response_data = response.read()
                content_type = response.headers.get('Content-Type', '')
                
                # 判断是否为JSON响应
                if content_type.startswith('application/json') or content_type.startswith('text/'):
                    try:
                        result = json.loads(response_data.decode('utf-8'))
                        
                        # 检查微信API错误
                        if 'errcode' in result and result['errcode'] != 0:
                            error_msg = self._get_error_message(result['errcode'])
                            raise Exception(f"{error_msg} (错误码: {result['errcode']})")
                        
                        return result
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # 如果JSON解析失败，可能是二进制数据，继续下面的处理
                        pass
                
                # 处理二进制响应（图片、音频、视频等素材）
                return {
                    'binary_data': response_data,
                    'headers': dict(response.headers),
                    'content_type': content_type,
                    'content_length': len(response_data)
                }
                
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP请求失败，状态码: {e.code}")
        except urllib.error.URLError as e:
            raise Exception(f"网络连接错误: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("API返回的数据格式错误")
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        获取稳定访问令牌
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            str: 访问令牌
        """
        url = f"{self.API_BASE_URL}/cgi-bin/stable_token"
        payload = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret,
            'force_refresh': force_refresh
        }
        
        result = self._send_request(url, require_token=False, payload=payload)
        return result['access_token']
    
    def upload_material(self, media_type: str, file_data: bytes, filename: str = None, title: str = None, introduction: str = None) -> Dict[str, Any]:
        """
        上传永久素材
        
        Args:
            media_type: 媒体类型 (image, voice, video, thumb)
            file_data: 文件数据
            filename: 文件名（可选）
            title: 视频标题（视频类型必需）
            introduction: 视频介绍（视频类型必需）
            
        Returns:
            Dict: 上传结果
        """
        url = f"{self.API_BASE_URL}/cgi-bin/material/add_material"
        params = {'type': media_type}
        
        # 如果提供了文件名，使用元组格式；否则只传文件数据
        if filename:
            files = {'media': (file_data, filename)}
        else:
            files = {'media': file_data}
        
        payload = {}
        
        if media_type == 'video' and title and introduction:
            payload['description'] = json.dumps({
                'title': title,
                'introduction': introduction
            })
        
        return self._send_request(url, params=params, files=files, payload=payload if payload else None)
    
    def get_material(self, media_id: str) -> Dict[str, Any]:
        """
        获取永久素材
        
        Args:
            media_id: 媒体ID
            
        Returns:
            Dict: 素材信息
        """
        url = f"{self.API_BASE_URL}/cgi-bin/material/get_material"
        payload = {'media_id': media_id}
        
        return self._send_request(url, payload=payload)
    
    def delete_material(self, media_id: str) -> Dict[str, Any]:
        """
        删除永久素材
        
        Args:
            media_id: 媒体ID
            
        Returns:
            Dict: 删除结果
        """
        url = f"{self.API_BASE_URL}/cgi-bin/material/del_material"
        payload = {'media_id': media_id}
        
        return self._send_request(url, payload=payload)
    
    def create_draft(self, articles: str) -> Dict[str, Any]:
        """
        创建草稿
        
        Args:
            articles: 文章数据JSON字符串
            
        Returns:
            Dict: 创建结果
        """
        url = f"{self.API_BASE_URL}/cgi-bin/draft/add"
        
        try:
            articles_data = json.loads(articles)
            payload = {'articles': articles_data}
        except json.JSONDecodeError:
            raise Exception("文章数据格式错误，请提供有效的JSON字符串")
        
        return self._send_request(url, payload=payload)
    
    def publish_draft(self, media_id: str) -> Dict[str, Any]:
        """
        发布草稿
        
        Args:
            media_id: 草稿媒体ID
            
        Returns:
            Dict: 发布结果
        """
        url = f"{self.API_BASE_URL}/cgi-bin/freepublish/submit"
        payload = {'media_id': media_id}
        
        return self._send_request(url, payload=payload)
    
    def upload_image(self, file_data: bytes, filename: str = None) -> Dict[str, Any]:
        """
        上传图文消息图片
        
        Args:
            file_data: 图片文件数据
            filename: 文件名（可选）
            
        Returns:
            Dict: 上传结果，包含图片URL
        """
        url = f"{self.API_BASE_URL}/cgi-bin/media/uploadimg"
        
        # 如果提供了文件名，使用元组格式；否则只传文件数据
        if filename:
            files = {'media': (file_data, filename)}
        else:
            files = {'media': file_data}
        
        return self._send_request(url, files=files)
    
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
            40009: '不合法的图片文件大小',
            40010: '不合法的语音文件大小',
            40011: '不合法的视频文件大小',
            40012: '不合法的缩略图文件大小',
            40013: '不合法的AppID',
            40014: '不合法的access_token',
            40113: '不支持的媒体文件格式',
            40164: '调用接口的IP地址不在白名单中，请在微信公众平台后台添加服务器IP到白名单',
            40015: '不合法的菜单类型',
            40016: '不合法的按钮个数',
            40017: '不合法的按钮个数',
            40018: '不合法的按钮名字长度',
            40019: '不合法的按钮KEY长度',
            40020: '不合法的按钮URL长度',
            40021: '不合法的菜单版本号',
            40022: '不合法的子菜单级数',
            40023: '不合法的子菜单按钮个数',
            40024: '不合法的子菜单按钮类型',
            40025: '不合法的子菜单按钮名字长度',
            40026: '不合法的子菜单按钮KEY长度',
            40027: '不合法的子菜单按钮URL长度',
            40028: '不合法的自定义菜单使用用户',
            40029: '不合法的oauth_code',
            40030: '不合法的refresh_token',
            40031: '不合法的openid列表',
            40032: '不合法的openid列表长度',
            40033: '不合法的请求字符，不能包含\\uxxxx格式的字符',
            40035: '不合法的参数',
            40038: '不合法的请求格式',
            40039: '不合法的URL长度',
            40050: '不合法的分组id',
            40051: '分组名字不合法',
            40117: '分组名字不合法',
            40118: 'media_id大小不合法',
            40119: 'button类型错误',
            40120: 'button类型错误',
            40121: '不合法的media_id类型',
            40132: '微信号不合法',
            40137: '不支持的图片格式',
            40155: '请勿添加其他公众号的主页链接',
            41001: '缺少access_token参数',
            41002: '缺少appid参数',
            41003: '缺少refresh_token参数',
            41004: '缺少secret参数',
            41005: '缺少多媒体文件数据',
            41006: '缺少media_id参数',
            41007: '缺少子菜单数据',
            41008: '缺少oauth code',
            41009: '缺少openid',
            42001: 'access_token超时，请检查access_token的有效期',
            42002: 'refresh_token超时',
            42003: 'oauth_code超时',
            42007: '用户修改微信密码，accesstoken和refreshtoken失效，需要重新授权',
            43001: '需要GET请求',
            43002: '需要POST请求',
            43003: '需要HTTPS请求',
            43004: '需要接收者关注',
            43005: '需要好友关系',
            43019: '需要将接收者从黑名单中移除',
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
        45047: '客服接口下行条数超过上限',
            46001: '不存在媒体数据',
            46002: '不存在的菜单版本',
            46003: '不存在的菜单数据',
            46004: '不存在的用户',
            47001: '解析JSON/XML内容错误',
            48001: 'api功能未授权，请确认公众号已获得该接口，可以在公众平台官网-开发者中心页中查看接口权限',
            48002: '粉丝拒收消息（粉丝在公众号选项中，关闭了"接收消息"）',
            48004: 'api接口被封禁，请登录mp.weixin.qq.com查看详情',
            48005: 'api禁止删除被自动回复和自定义菜单引用的素材',
            48006: 'api禁止清零调用次数，因为清零次数达到上限',
            48008: '没有该类型消息的发送权限',
            50001: '用户未授权该api',
            50002: '用户受限，可能是违规后接口被封禁',
            50005: '用户未关注公众号',
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
            65316: '该公众号的菜单设置了过多的域名外跳（最多跳转到3个域名的链接）',
            65317: '不合法的URL',
            9001001: 'POST数据参数不合法',
            9001002: '远端服务不可用',
            9001003: 'Ticket不合法',
            9001004: '获取摇周边用户信息失败',
            9001005: '获取商户信息失败',
            9001006: '获取OpenID失败',
            9001007: '上传文件缺失',
            9001008: '上传素材的文件类型不合法',
            9001009: '上传素材的文件尺寸不合法',
            9001010: '上传失败',
            9001020: '帐号不合法',
            9001021: '已有设备激活率低于50%，不能新增设备',
            9001022: '设备申请数不合法，必须为大于0的数字',
            9001023: '已存在审核中的设备ID申请',
            9001024: '一次查询设备ID数量不能超过50',
            9001025: '设备ID不合法',
            9001026: '页面ID不合法',
            9001027: '页面参数不合法',
            9001028: '一次删除页面ID数量不能超过10',
            9001029: '页面已应用在设备中，请先解除应用关系再删除',
            9001030: '一次查询页面ID数量不能超过50',
            9001031: '时间区间不合法',
            9001032: '保存设备与页面的绑定关系参数错误',
            9001033: '门店ID不合法',
            9001034: '设备备注信息过长',
            9001035: '设备申请参数不合法',
            9001036: '查询起始值begin不合法'
        }
        
        return error_messages.get(errcode, f'未知错误码: {errcode}')