<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

## ✨ nonebot-plugin-fortnite ✨
[![LICENSE](https://img.shields.io/github/license/fllesser/nonebot-plugin-fortnite.svg)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-fortnite.svg)](https://pypi.python.org/pypi/nonebot-plugin-fortnite)
[![python](https://img.shields.io/badge/python-3.10|3.11|3.12|3.13|3.14-blue.svg)](https://www.python.org)
[![uv](https://img.shields.io/badge/package%20manager-uv-black?style=flat-square&logo=uv)](https://github.com/astral-sh/uv)
<br/>
[![ruff](https://img.shields.io/badge/code%20style-ruff-black?style=flat-square&logo=ruff)](https://github.com/astral-sh/ruff)
[![pre-commit](https://results.pre-commit.ci/badge/github/fllesser/nonebot-plugin-fortnite/master.svg)](https://results.pre-commit.ci/latest/github/fllesser/nonebot-plugin-fortnite/master)
[![codecov](https://codecov.io/gh/fllesser/nonebot-plugin-fortnite/graph/badge.svg?token=2F8LMGXW1O)](https://codecov.io/gh/fllesser/nonebot-plugin-fortnite)
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

|             配置项             | 必填  | 默认值  |                        说明                        |
| :----------------------------: | :---: | :-----: | :------------------------------------------------: |
|       fortnite_api_key         |  是   |   ''    |                      api-key                       |
| fortnite_screenshot_from_github |  否   |  false  | 是否从 GitHub 分支下载截图（而非实时截图） |

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
