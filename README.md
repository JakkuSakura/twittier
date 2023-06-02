# Twittier

一些推特的实用小工具，方便用于推特抽奖等。

包含 `status_dumper` 和 `lucky_draw` 两个工具。

- status_dumper

    - 用于导出推文的评论、喜欢、引用、转推和动态（包含所有的）。

- lucky_draw

    - 用于抽奖，可以从 `status_dumper` 产生的动态（包含所有的）中抽取指定数量的用户。

## 安装

```shell
pip install twittier
```

## 用法

- status_dumper

  - 使用浏览器（Chrome/Edge等）打开你的推文，按下 `F12` 打开开发者工具，切换到 `Network/网络` 选项卡后并刷新页面。
  - 将页面一直往下滚动，直到所有的回复都显示出来
  - 点开 `XXX则转推` 和 `XXX个喜欢` 和 `XXX引用`，在打开的页面一直往下滚动，直到所有显示出来。
  - 点击开发者工具的 `下箭头` 图表，将所有的请求导出为 `HAR` 文件
  - 使用命令行命令 `python -m twittier status_dumper <HAR文件路径>` 运行程序
  - 程序会在当前目录下生成 `comments.json`、`likes.json`、`quotes.json`、`retweets.json` 和 `dynamic.txt` 文件，分别对应评论、喜欢、引用、转推和动态（包含所有的）。

- lucky_draw
  - 使用命令行命令 `python -m twittier draw <动态文件路径> -p [抽取数量列表]` 运行程序
  - 程序将会输出抽取的用户列表以及抽到的用户名单。
  - 例如：`python -m twittier draw dynamic.txt -p 1 2 3`，将会从 `dynamic.txt` 中抽取 1 个、2 个和 3 个用户。
  - 也可以添加 `-r` 来限定抽取的范围。默认为 `评论+喜欢+转推`
  - 例如：`python -m twittier draw dynamic.txt -p 1 2 3 -r like`，将会从 `dynamic.txt` 中抽取 1 个、2 个和 3 个`喜欢了推文`的用户。
  - 例如：`python -m twittier draw dynamic.txt -p 1 2 3 -r like retweet`，将会从 `dynamic.txt` 中抽取 1 个、2 个和 3 个`喜欢了推文并且转推了推文`的用户。

