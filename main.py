from dify_plugin import Plugin, DifyPluginEnv

# 创建插件实例
# 微信公众号API通常响应较快，设置30秒超时
app = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=30))

# 插件入口点
if __name__ == '__main__':
    app.run()