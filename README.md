### 概述

百工汇智PDM拓展程序是一款旨在简化BOM表上传的拓展程序
- 允许用户将已有的BOM表快速的上传到Aras Innovator平台，实现项目的共享与存储

### 下载安装及运行方法

1. 访问Aras Innovator，在左侧菜单中选择 **文件下载**
2. 在其中选择 **PDM拓展程序** 下载
3. 将下载的压缩包进行解压
4. 运行 **window.exe**

### 编译器

该拓展程序使用 **Python 3.12** 进行编译

### 运行依赖的外部库

- requests
- tkinter
- sv_ttk
- threading

### 开发方法

- 通过 **Aras Innovator RESTful API** 进行信息和文件的传输
- 通过 **Tkinter** 搭建用户界面，并通过 **Sun-Valley-ttk-theme** 美化界面
- 运行文件通过 **Pyinstaller** 生成，文件夹中包含了运行所需的外部库

### 隐私

- 登录后，拓展程序将保存用户名
- 若选择记住密码，则同时会保存用户的密码

### 参考文件

- 官方文档
  - [Aras Innovator 安装手册](https://aras.com/wp-content/uploads/2024/06/Aras-Innovator-2024-Release-Installation-Guide.pdf)
  - [Aras Innovator 二次开发手册](https://media.aras.com/wp-content/uploads/2024/06/Aras-Innovator-2024-Release-Installation-Guide.pdf)
  - [Aras Innovator API 手册](https://media.aras.com/wp-content/uploads/2024/05/Aras-Innovator-2024-Release-RESTful-API.pdf)

- 验证登录样例
  - [通过 RESTful API 验证登录](https://github.com/ArasLabs/rest-auth-example)

- 上传文件样例
  - [通过 Aras Innovator RESTful API 上传文件](https://aras.com/en/blog/uploading-files-via-the-aras-innovator-rest-api)
  - [官方上传文件的样例 JavaScript](https://github.com/ArasLabs/rest-upload-example)

- Sun-Valley-ttk-theme
  - [sv_ttk 的 Github 地址](https://github.com/rdbende/Sun-Valley-ttk-theme)
  - [sv_ttk 的样例](https://github.com/rdbende/Sun-Valley-ttk-examples)

