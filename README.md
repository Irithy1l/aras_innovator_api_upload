### Overview

Baitech PDM extension is an extension designed to simplify BOM upload
- Allow users to quickly upload existing BOMs to the Aras Innovator platform to achieve project sharing and storage

### Download, install and run methods

1. Access Aras Innovator and select **File Download** in the left menu
2. Select **PDM extension** Download
3. Unzip the downloaded compressed package
4. Run **window.exe**

### Compiler

This extension is compiled with **Python 3.12**

### Run dependent external libraries

- requests
- tkinter
- sv_ttk
- threading

### Development method

- Transmit information and files through **Aras Innovator RESTful API**
- Build the user interface through **Tkinter** and beautify the interface through **Sun-Valley-ttk-theme**
- Run the file through **Pyinstaller** generated, the folder contains the external libraries required for running

### Privacy

- After logging in, the extension will save the username
- If you choose to remember the password, the user's password will also be saved

### Reference files

- Official documents
  - [Aras Innovator 2024 Release Installation Guide](https://aras.com/wp-content/uploads/2024/06/Aras-Innovator-2024-Release-Installation-Guide.pdf)
  - [Aras Innovator 29 Programmer's Guide](https://www.aras.com/community/DocumentationLibrary/ALL%20PDFs/Flare%20PDF/Flare%20PDF/Innovator%2029/Aras%20Innovator%2029%20-%20Programmer's%20Guide.pdf)
  - [Aras Innovator 2024 Release RESTful API](https://media.aras.com/wp-content/uploads/2024/05/Aras-Innovator-2024-Release-RESTful-API.pdf)

- Authentication login example
  - [OAuth and the Aras RESTful API](https://github.com/ArasLabs/rest-auth-example)

- Upload file example
  - [Uploading Files via the Aras Innovator REST API](https://aras.com/en/blog/uploading-files-via-the-aras-innovator-rest-api)
  - [Official upload file example JavaScript](https://github.com/ArasLabs/rest-upload-example)

- Sun-Valley-ttk-theme
  - [sv_ttk Github](https://github.com/rdbende/Sun-Valley-ttk-theme)
  - [sv_ttk Example](https://github.com/rdbende/Sun-Valley-ttk-examples)

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
  - [Aras Innovator 二次开发手册](https://www.aras.com/community/DocumentationLibrary/ALL%20PDFs/Flare%20PDF/Flare%20PDF/Innovator%2029/Aras%20Innovator%2029%20-%20Programmer's%20Guide.pdf)
  - [Aras Innovator API 手册](https://media.aras.com/wp-content/uploads/2024/05/Aras-Innovator-2024-Release-RESTful-API.pdf)

- 验证登录样例
  - [通过 RESTful API 验证登录](https://github.com/ArasLabs/rest-auth-example)

- 上传文件样例
  - [通过 Aras Innovator RESTful API 上传文件](https://aras.com/en/blog/uploading-files-via-the-aras-innovator-rest-api)
  - [官方上传文件的样例 JavaScript](https://github.com/ArasLabs/rest-upload-example)

- Sun-Valley-ttk-theme
  - [sv_ttk 的 Github 地址](https://github.com/rdbende/Sun-Valley-ttk-theme)
  - [sv_ttk 的样例](https://github.com/rdbende/Sun-Valley-ttk-examples)

