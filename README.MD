Auto_Record_Matsuri [![Build Status](https://travis-ci.org/fzxiao233/Auto_Record_Matsuri.svg?branch=master)](https://travis-ci.org/fzxiao233/Auto_Record_Matsuri)
====
此程序能够自动监控夏妹直播并下载当前的直播视频（其实你也可以修改其中的频道编号来监控其他VTB[臭DD]

    
功能
----
- 自动监控Youtube|Mirrativ|Openrec开播
- 自动下载直播视频（即使不留档也能下载）
- 自动上传到百度云并获取分享链接
- 自动插入数据库存储


使用
------
- 首次启动或更新时

	    $ pip3 install -r requirements.txt
- 执行程序

	    $ python main.py
	    
- 使用机器人需要下载酷Q Air 并安装 HTTP API（https://cqhttp.cc/）

- 使用自动上传分享需要手动在BaiduPCS-Go文件夹中放入文件，并登录（https://github.com/iikira/BaiduPCS-Go）

- 使用数据库需要

        $ python web.py
支持
------
- 更多设置，请编辑config.py


有问题就发Issues吧，有时间就修（鸽了
