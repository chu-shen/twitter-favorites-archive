# Twitter Favorites(Likes) Archive
A series of scripts to archive metadata and medias of your Twitter Favorites(Likes).

使用Python实现，原版见[15cm/twitter-favorites-archive](https://github.com/15cm/twitter-favorites-archive)

- 使用sqlite数据库存储进度，效率更高
- 暂不支持获取站外图

## Prerequisites

### Twitter API
Register an App on [Twitter Developer](https://developer.twitter.com/apps) and get
access credentials in the "Keys and Tokens" tab of your App's page.

### Environment

```shell
conda install --file env_conda.txt

pip install -r env_pip.txt
```

## Usage

Rename `config.template.py` to `config.py` and customize it with:
- Twitter API credentials
- SAVE_PATH：保存路径，默认当前目录

运行：`python getTweetMedia.py`

## Use cases
### PhotoPrism
I import the media files gathered by this project into [PhotoPrism](https://github.com/photoprism/photoprism) so that I can browse images of my Twitter Favorites in a more flexible way.

![PhotoPrism Use Case Screenshot](./assets/images/use-case-photoprism-0.png)


## 致谢

感谢以下项目：

- [15cm/twitter-favorites-archive](https://github.com/15cm/twitter-favorites-archive)
- [LeoHsiao1/pyexiv2](https://github.com/LeoHsiao1/pyexiv2)
- [chatgpt](https://chat.openai.com/chat)