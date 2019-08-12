Auto_Record_Matsuri [![Build Status](https://travis-ci.org/fzxiao233/Auto_Record_Matsuri.svg?branch=master)](https://travis-ci.org/fzxiao233/Auto_Record_Matsuri)
====
此程序能够自动监控夏妹直播并下载当前的直播视频（其实你也可以修改其中的频道编号来监控其他VTB[臭DD]
目前我已经在VPS上部署了，你可以通过访问https://matsuri.design 获取录播

本程序已彻底拆分为了两个部分，详见[live_monitor_worker](https://github.com/fzxiao233/live_monitor_worker)和[live_monitor_server](https://github.com/fzxiao233/live_monitor_server),故本项目不再维护。

特性
----
- 使用多线程进行监控

- 通过多进程启动下载和上传任务

    
功能
----
- 自动监控Youtube|Openrec|Mirrativ|Twitcasting平台的直播
- 自动监控Bilibili熟肉更新
- 自动发送直播通知至QQ群（延迟极低，在检测时间设置为15s时）
- 自动即时抓流下载直播视频（从此杜绝苦苦哀求录播man）
- 自动将下载的视频上传并设置分享到百度云
- 顺带维护了一个网页用来发布直播存档


使用
------
- 请务必在启动前编辑config.py文件(详细配置方法见下文)

- 首次启动或更新时

	    $ pip3 install -r requirements.txt
- 执行程序

	    $ python run.py
	    
- 使用机器人需要下载[酷Q Air](https://cqhttp.cc/) 并安装 HTTP API

- 使用自动上传分享需要手动在[BaiduPCS-Go](https://github.com/iikira/BaiduPCS-Go)文件夹中放入文件，并登录

支持
------

### 配置方法

- 复制config_example.py文件为config.py

- 参照下列注释编辑文件

		config = {
			'enable_proxy': False, # 是否使用代理检测
			'proxy': '', # 代理服务地址，应使用http代理
			'ddir': '/home/ubuntu/Matsuri', # 主存储目录，下文可以设置子目录
			'sec': 15, # 检测间隔时间 单位秒
			'error_sec': 5, # 错误重试时间 单位秒
			'enable_bot': False, # 是否启动bot通知
			'bot_host': '', # bot的HTTPAPI地址
			'group_id': [], # bot需要通知的群号
			'bot_token': '', # bot的Token验证
			'enable_upload': True, # 是否启动上传功能
			'upload_by': 'bd', # 上传通过 bd：百度云 s3： 任意兼容s3api的云存储
			'enable_mongodb': False, # 是否启动mongodb用于记录（youtube_temp模块依赖项
			's3_server': '', # s3服务器地址
			's3_access_key': '',
			's3_secret_key': '',
			# Youtube模块
			'youtube': {
				'enable': True, # 是否启用模块
				'enable_temp': False, # 是否启用补充功能
				'enable_temp_bot_notice': True, # 补充功能是否发送bot通知
				'enable_temp_download': True, # 补充功能是否下载视频
				'quality': '720p', # 默认下载画质
				'api_key': '', # Youtube API key 不填入也可使用
				# 监控对象
				'users': [
					{
						'target_id': 'UCQ0UDLQCjY0rmuxCDE38FGg', # 频道号
						'bot_notice': True, # 是否启用bot通知
						'download': True # 是否下载
					},
					{
						'target_id': 'UCl_gCybOJRIgOXw6Qb4qJzQ',
						'ddir': 'rushia',
						'bot_notice': False,
						'download': True
					}
				]
			},
			'twitcasting': {
				'enable': True,
				'users': [
					{
						'target_id': 'natsuiromatsuri',
						'bot_notice': True,
						'download': True
					}
				]
			},
			'mirrativ': {
				'enable': True,
				'users': [
					{
						'target_id': '3264432',
						'bot_notice': True,
						'download': True
					}
				]
			},
			'openrec': {
				'enable': True,
				'users': [
					{
						'target_id': 'natsuiromatsuri',
						'bot_notice': True,
						'download': True
					}
				]
			},
			'bilibili': {
				'enable': True,
				'users': [
					{
						'target_id': '336731767',
						'bot_notice': True,
						'download': True
					}
				]
			}
		}

- 有问题或者新功能请求请发Issues
