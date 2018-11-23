# OpenERP8.0中国版本。

目标
-------------
降低OpenERP中国社区项目的参与门槛

面向群体和职责划分
-------------

初级程序员 -- 将github上官方项目变更人工复制到本项目，并加中文变更记录

用户/顾问   -- 提交实施或日常使用过程中发现的issue

高级程序员 --  解决issue并将修改推送到github上的官方项目

汉化参与者 -- 持续更新汉化po文件

﻿基于 OpenERP20140919 源码包 29e08a2

持续跟进官方库  https://github.com/odoo/odoo/commits/8.0
  
增加有用的社区模块

合并官方未接受的合并请求

管理中文社区发现的bug和提交的patch

如何参与开发：
-------------

1. 在openerp-china项目上点击fork按钮，形成你自己的项目

2. clone你自己的项目到本地

3. 添加 osbzr 的 remote 只需要做一次
git remote add osbzr http://git.oschina.net/osbzr/openerp-china.git

4. 拉 主干代码到本地
git fetch osbzr

5. 合并 主干代码到本地
git merge osbzr/master

6. 推送 本地合并后的代码到 fork 项目
git push origin master

7. 向主项目提交合并请求

网友评论：OpenERP中国版和官方版有什么区别？
=============================================

瘦身了

应该还加了些东西

去掉了点bug

另外据说处理bug的速度快过官方

最主要是, 可以用母语报BUG.

可以用母语看更新记录

还附带完整中文汉化包
