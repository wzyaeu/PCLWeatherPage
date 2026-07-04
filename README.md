# Weather 天气预报介绍

本项目是一个PCL的主页项目，旨在展现天气信息。

![展示](https://raw.githubusercontent.com/wzyaeu/PCLWeatherPage/refs/heads/main/image/rm1.png)

# 初始化指引

## 0.前提提要

- 项目作者不对你使用API产生的任何费用付费。
- 你的电脑时间需要精确，基本无太大偏差。

## 1.生成初始文件

先生成一些初始文件，方便填写。

1. 运行`main.py`。
    ```dash
    python main.py
    ```
2. 将在目录下生成`priv.txt`、`pub.txt`、`apihost.txt`、`pid.txt`、`tid.txt`、`port.txt`、`location.txt`。
3. 关闭程序。

## 2. 申请 API Key

本项目由和风天气驱动，需要在API官网申请到API Key。

1. 打开官网并注册 [注册官网](https://id.qweather.com/#/register?lang=zh)  
   需要邮箱、手机号，无需实名。
2. 注册后进入控制台 [控制台](https://console.qweather.com/home?lang=zh)
3. 点击左侧列表中的 [项目管理](https://console.qweather.com/project?lang=zh)
4. 点击右侧按钮 [创建项目](https://console.qweather.com/project/new?lang=zh)
5. 输入一个项目名字，PCLWeatherPage，点击保存。
6. 点击右侧按钮 创建凭据。
7. 输入一个凭据名称，PCLHomePage。
8. 你可以在任何地方生成一个Ed25519密钥，推荐在[此网页](https://tools.top/key-generator.html)中生成（选择PEM格式）。
9. 保存你的私钥在`priv.txt`里，保存你的公钥在`pub.txt`里。
10. 复制你的公钥，粘贴在上传公钥一栏里。
11. 选择启用的API：建议全选，未来的项目可能需要更多的API。如果你不想因为自己的API的启用导致花钱，你也可以启用除辐射、海洋、热带气旋的API（剩下的API有免费额度），或者只启用你需要的API。
12. 点击保存，生成你的凭据。

## 3. 获取 API 请求所需内容

1. 生成后会到一个新的页面，点击左侧列表的设置。
2. 找到你的API Host，格式类似`abc1234xyz.def.qweatherapi.com`。
3. 复制你的API Host，粘贴至目录下的`apihost.txt`里。
4. 点击左侧列表中的项目管理，点进去你的项目。
5. 找到项目ID并粘贴到`pid.txt`里。
5. 继续点击你的凭据，找到凭据ID并粘贴到`tid.txt`里。

## 4.选定你的位置

1. 跳转至[中国地区城市ID列表](https://github.com/qwd/LocationList/blob/master/China-City-List-latest.csv)通过第3列和第8列找到你的地区。
2. 复制这个地区第一列的`Location_ID`。
3. 粘贴至`location.txt`中。

> 虽然你也可以选择外国地区，但那里的天气数据并不完整

## 5.运行

所有的项目已经配置完成，现在可以运行了。

1. 确保生成的每一个文件都已填好内容（`port.txt`会自动写入`2521`）
2. 运行`main.py`
3. 在PCL里的`设置 - 个性化 - 主页`中选择`联网更新`，填入地址`http://localhost:{port}`
   > `{port}`处填入`port.txt`的内容
4. 完成！

## 运行时注意

- 不要乱动`nowweather-data.txt`、`nowweather-time.txt`、`futwweather-data.txt`、`futwweather-time.txt`，否则会导致不必要的api开销。