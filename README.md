# Twittier Http Parser

一个小工具用来分析twitter的http请求，方便找出哪些人`喜欢/转发/回复/引用`了你的推文。

## 用法

- 使用浏览器（Chrome/Edge等）打开你的推文，按下 `F12` 打开开发者工具，切换到 `Network/网络` 选项卡
- 将页面一直往下滚动，直到所有的回复都显示出来
- 点开 `XXX则转推` 和 `XXX个喜欢` 和 `XXX引用`，在打开的页面一直往下滚动，直到所有显示出来。
- 点击开发者工具的 `下箭头` 图表，将所有的请求导出为 `HAR` 文件
- 使用命令行命令 `python -m twittier_http_parser <HAR文件路径>` 运行程序
- 程序会在当前目录下生成 `comments.json`、`likes.json`、`quotes.json`、`retweets.json` 和 `dynamic.txt` 文件，分别对应评论、喜欢、引用、转推和动态（包含所有的）。

