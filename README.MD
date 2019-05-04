Auto_Record_Matsuri [![Build Status](https://travis-ci.org/fzxiao233/Auto_Record_Matsuri.svg?branch=master)](https://travis-ci.org/fzxiao233/Auto_Record_Matsuri)
====
此程序能够自动监控夏妹直播并下载当前的直播视频（其实你也可以修改其中的频道编号来监控其他VTB[臭DD]
目前我已经在VPS上部署了，你可以通过访问http://matsuri.fzxiao.tw 获取录播

特性
----
- 使用多进程模型，同时监控多个Vtuber占用较低（DD）

    
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
- 请务必在启动前编辑config.py文件

- 首次启动或更新时

	    $ pip3 install -r requirements.txt
- 执行程序

	    $ python run.py
	    
- 使用机器人需要下载[酷Q Air](https://cqhttp.cc/) 并安装 HTTP API

- 使用自动上传分享需要手动在[BaiduPCS-Go](https://github.com/iikira/BaiduPCS-Go)文件夹中放入文件，并登录

支持
------
- 有问题或者新功能请求请发Issues
