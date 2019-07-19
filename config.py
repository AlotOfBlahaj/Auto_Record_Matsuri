# 是否启用代理
enable_proxy = 0
# 代理地址，应使用http代理
proxy = '127.0.0.1:10800'
# 保存位置
ddir = '/root/Matsuri'  # 这里后边不应该有斜杠
# YoutubeAPI3Key 申请地址：https://console.developers.google.com/apis/library/youtube.googleapis.com
api_key = ''
# 监测频道ID 可填入多个频道，格式为['第一个地址', '第二个地址']
channel_id = ['UCQ0UDLQCjY0rmuxCDE38FGg']  # UCQ0UDLQCjY0rmuxCDE38FGg
# mirrativ用户ID
userid = ['3264432']  # 3264432
# Openrec用户ID
oprec_id = ['natsuiromatsuri']  # natsuiromatsuri
# Twitcasting用户ID
twitcasting_ld = ['natsuiromatsuri']
# Bilibili用户ID
bilibili_id = ['336731767']
# 检测间隔时间（s）
sec = 15
# 错误间隔时间（s）
sec_error = 5
# 是否启用mongodb数据库 0/1 注：如未部署请与youtube_temp模块一起保持关闭
enable_db = 0
# 是否开启youtube监控 0/1
enable_youtube = 1
# 是否启用youtube补充模块 0/1 注：如未部署mongodb请保持关闭
enable_youtube_temp = 0
# 是否开启mirrativ监控 0/1
enable_mirrativ = 1
# 是否开启openrec监控 0/1
enable_openrec = 1
# 是否开启twitcasting监控 0/1
enable_twitcasting = 1
# 是否开启bilibili熟肉更新监控 0/1
enable_bilibili = 1
# 机器人开关
enable_bot = 0
# 酷Q机器人HTTPAPI接口
host = '127.0.0.1:5700'
# 要发送消息的QQ群号，暂时不支持多群
group_id = ['']
# 是否开启上传 0/1
enable_upload = 0
# 选择上传方式 可填入 'bd', 's3'
upload_by = 's3'
# S3服务器
s3_server = 'http://s3.us-west-1.wasabisys.com/'
# S3 access_key
s3_access_key = ''
# S3 secret_key
s3_secret_key = ''
# Youtube画质设定（其他平台均为最高画质
youtube_quality = 'best'  # best为最高画质，可选：720p, best
