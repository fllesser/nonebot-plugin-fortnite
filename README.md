<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

## ✨ nonebot-plugin-fortnite ✨

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/fllesser/nonebot-plugin-fortnite.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-fortnite">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-fortnite.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg" alt="python">

</div>



## 📖 介绍

堡垒之夜战绩/季卡/商城/vb图查询插件

自用插件，发来凑个数（万一玩nb的也有人玩堡垒的呢

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-fortnite --upgrade

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-fortnite
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-fortnite
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-fortnite
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-fortnite
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_fortnite"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|      配置项      | 必填  | 默认值 |  说明   |
| :--------------: | :---: | :----: | :-----: |
| fortnite_api_key |  是   |   ''   | api-key |

## 🎉 使用
### 指令表
|    指令    | 权限  | 需要@ | 范围  |   说明   |
| :--------: | :---: | :---: | :---: | :------: |
| [生涯]战绩 |   -   |  否   |   -   | 顾名思义 |
| [生涯]季卡 |   -   |  否   |   -   | 顾名思义 |
|    商城    |   -   |  否   |   -   | 顾名思义 |
|    vb图    |   -   |  否   |   -   | 顾名思义 |
|  更新商城  | 主人  |  否   |   -   | 顾名思义 |
|  更新vb图  | 主人  |  否   |   -   | 顾名思义 |
