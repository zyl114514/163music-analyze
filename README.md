# 网易云音乐偏好分析
## 目录

 1. 项目描述
 2. 所需模块
 3. 安装
 4. 运行
 5. 贡献者们
 6. 项目展示

## 项目描述
该项目的主要功能是通过输入用户的网易云音乐id获取用户的歌单，根据用户的歌单中歌曲的风格标签以及歌手来分析用户的听歌偏好，将其听歌偏好可视化，并为其推荐三首符合其听歌偏好的歌曲。还能获取用户收藏歌曲的评论，并从中提取关键词。


## 所需模块

 - 网易云音乐API
 - node.js
 - flask框架
 - 其他python库


## 安装

    git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
    cd NeteaseCloudMusicApi
    npm install
    pip install requests
    pip install flask
    pip install alive_progress
    pip install wordcloud
    pip install jieba


## 运行
进入项目文件夹

    cd NeteaseCloudMusicApi

运行网易云音乐api（需要安装node.js）

    node app.js

在IDE中点击运行或输入

    python3 app.py

成功运行后，进入本地服务器https://localhost:5000
在输入框中输入你想分析的用户id，点击提交按钮，等待分析程序运行。运行时间取决于该用户歌单中歌曲的数量，约2-4首歌每秒钟。

## 贡献者们

感谢网易云音乐API的制作者Binaryify，使项目可以完成更多功能。

## 项目展示

本项目视频已上传至bilibili
https://www.bilibili.com/video/BV1JN411r7UQ/?spm_id_from=333.999.0.0&vd_source=9a483e3b8f04b360bebe17679e9cc7c6
