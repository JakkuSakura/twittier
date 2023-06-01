import argparse
import json
import logging
import sys
from typing import Optional, List

from ._types import RequestType


def get_type_by_url(url: str) -> Optional[RequestType]:
    for t in RequestType:
        if t.value in url:
            return t
    return None


likes: List[dict] = []
retweets: List[dict] = []
comments: List[dict] = []
quotes: List[dict] = []

dynamic: str = ''

def get_favorite_users(response: dict):
    global likes
    global dynamic
    data = json.loads(response['content']['text'])
    if 'data' in data:
        data = data['data']
    if not 'favoriters_timeline' in data:
        return
    try:
        entries = data['favoriters_timeline']['timeline']['instructions'][0]['entries']
    except KeyError:
        return
    for entry in entries:
        try:
            legacy = entry['content']['itemContent']['user_results']['result']['legacy']
        except KeyError:
            continue
        dynamic += f'@{legacy["screen_name"]} 喜欢了推文\n'
        likes.append(entry)


def get_retweeters(response: dict):
    global retweets
    global dynamic
    data = json.loads(response['content']['text'])
    if 'data' in data:
        data = data['data']
    if not 'retweeters_timeline' in data:
        return
    try:
        entries = data['retweeters_timeline']['timeline']['instructions'][0]['entries']
    except KeyError:
        return
    for entry in entries:
        try:
            legacy = entry['content']['itemContent']['user_results']['result']['legacy']
        except KeyError:
            continue
        dynamic += f'@{legacy["screen_name"]} 转推了推文\n'
        retweets.append(entry)


def get_comments(response: dict):
    global comments
    global dynamic
    data = json.loads(response['content']['text'])
    if 'data' in data:
        data = data['data']
    if not 'threaded_conversation_with_injections_v2' in data:
        return
    try:
        entries = data['threaded_conversation_with_injections_v2']['instructions'][0]['entries']
    except KeyError:
        return
    for entry in entries:
        if not entry['entryId'].startswith('conversationthread'):
            continue
        try:
            # print(json.dumps(entry, indent=4, ensure_ascii=False))
            # content / items / 0 / item / item / tweet_results / result / core / user_results / result / legacy
            # content / items / 0 / item / itemContent / tweet_results / result / core / user_results / result / legacy
            legacy = entry['content']['items'][0]['item']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']
        except KeyError:
            continue
        dynamic += f'@{legacy["screen_name"]} 评论了推文\n'
        comments.append(entry)


def get_quotes(response: dict):
    global quotes
    data = json.loads(response['content']['text'])
    try:
        tweets = data['globalObjects']['tweets']  # type: dict
    except KeyError:
        return
    for tweet in tweets.values():
        if 'quoted_status_id' in tweet:
            quotes.append(tweet)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(threadName)s/%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    parser = argparse.ArgumentParser(prog='twitter_http_parser')
    parser.add_argument('path', help='path to twitter .har file')
    args = parser.parse_args()

    with open(args.path, 'r', encoding='utf-8') as f:
        har = json.load(f)

    entries = har['log']['entries']

    for entry in entries:
        url = entry['request']['url']
        response = entry['response']

        req_type = get_type_by_url(url)
        if req_type is None:
            continue

        if req_type == RequestType.FAVORITERS:
            get_favorite_users(response)
        elif req_type == RequestType.RETWEETERS:
            get_retweeters(response)
        elif req_type == RequestType.COMMENT:
            get_comments(response)
        elif req_type == RequestType.QUOTES:
            get_quotes(response)

    with open('likes.json', 'w', encoding='utf-8') as f:
        json.dump(likes, f, ensure_ascii=False, indent=2)

    with open('retweets.json', 'w', encoding='utf-8') as f:
        json.dump(retweets, f, ensure_ascii=False, indent=2)

    with open('comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    with open('quotes.json', 'w', encoding='utf-8') as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)

    with open('dynamic.txt', 'w', encoding='utf-8') as f:
        f.write(dynamic)

    return 0


if __name__ == '__main__':
    sys.exit(main())
