TiebaWasher
===========

功能：

- 模拟登录wap版百度贴吧
- 定时刷新指定贴吧，抢先二楼回复;
- 贴吧签到
- 调用Simsimi机器人的“弱智能”回复【2014.09.12】

程序依赖：

- 基于Python2.7
- requests模块
- BeautifulSoup模块
- tornadohttpclient

使用说明：

1. 将`settings.py.example`改名为`settings.py`，打开该文件并按照其中说明完成相关配置。
2. 在终端中运行main.py。如果需要贴吧签到，则需要带上`-s`运行参数。
