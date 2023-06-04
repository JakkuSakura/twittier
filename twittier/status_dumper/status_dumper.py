import json
from typing import Optional, List, Any

from ._types import RequestType


def get_type_by_url(url: str) -> Optional[RequestType]:
    for t in RequestType:
        if t.value in url:
            return t
    return None


def get_favorite_users(response: dict):
    data = json.loads(response['content']['text'])
    if 'data' in data:
        data = data['data']
    if not 'favoriters_timeline' in data:
        return
    try:
        entries = data['favoriters_timeline']['timeline']['instructions'][0]['entries']
    except KeyError:
        return
    entry_rt = []
    dynamic_rt = []
    for entry in entries:
        try:
            legacy = entry['content']['itemContent']['user_results']['result']['legacy']
        except KeyError:
            continue
        entry_rt.append(entry)
        dynamic_rt.append(f'@{legacy["screen_name"]} 喜欢了推文')
    return entry_rt, dynamic_rt


def get_retweeters(response: dict):
    data = json.loads(response['content']['text'])
    if 'data' in data:
        data = data['data']
    if not 'retweeters_timeline' in data:
        return
    try:
        entries = data['retweeters_timeline']['timeline']['instructions'][0]['entries']
    except KeyError:
        return
    entry_rt = []
    dynamic_rt = []
    for entry in entries:
        try:
            legacy = entry['content']['itemContent']['user_results']['result']['legacy']
        except KeyError:
            continue
        entry_rt.append(entry)
        dynamic_rt.append(f'@{legacy["screen_name"]} 转推了推文')
    return entry_rt, dynamic_rt


def get_comments(response: dict):
    data = json.loads(response['content']['text'])
    if 'data' in data:
        data = data['data']
    if not 'threaded_conversation_with_injections_v2' in data:
        return
    try:
        entries = data['threaded_conversation_with_injections_v2']['instructions'][0]['entries']
    except KeyError:
        return
    entry_rt = []
    dynamic_rt = []
    for entry in entries:
        if not entry['entryId'].startswith('conversationthread'):
            continue
        try:
            legacy = \
                entry['content']['items'][0]['item']['itemContent']['tweet_results']['result']['core']['user_results'][
                    'result']['legacy']
        except KeyError:
            continue
        entry_rt.append(entry)
        dynamic_rt.append(f'@{legacy["screen_name"]} 评论了推文')
    return entry_rt, dynamic_rt


def get_quotes(response: dict):
    data = json.loads(response['content']['text'])
    try:
        tweets = data['globalObjects']['tweets']  # type: dict
    except KeyError:
        return
    rt = []
    for tweet in tweets.values():
        if 'quoted_status_id' in tweet:
            rt.append(tweet)
    return rt

def distinct_objects(objs: List[Any]) -> List[Any]:
    strs = set()
    for obj in objs:
        strs.add(json.dumps(obj, ensure_ascii=False))
    strs = list(strs)
    strs.sort()
    output = []
    for str in strs:
        output.append(json.loads(str))
    return output

def dumper(path: str) -> int:
    likes: List[dict] = []
    retweets: List[dict] = []
    comments: List[dict] = []
    quotes: List[dict] = []

    dynamic: List[str] = []

    with open(path, 'r', encoding='utf-8') as f:
        har = json.load(f)

    entries = har['log']['entries']

    for entry in entries:
        url = entry['request']['url']
        response = entry['response']

        req_type = get_type_by_url(url)
        if req_type is None:
            continue

        if req_type == RequestType.FAVORITERS:
            rt = get_favorite_users(response)
            if rt is None:
                continue
            e, d = rt
            likes += e
            dynamic.extend(d)
        elif req_type == RequestType.RETWEETERS:
            rt = get_retweeters(response)
            if rt is None:
                continue
            e, d = rt
            retweets += e
            dynamic.extend(d)
        elif req_type == RequestType.COMMENT:
            rt = get_comments(response)
            if rt is None:
                continue
            e, d = rt
            comments += e
            dynamic.extend(d)
        elif req_type == RequestType.QUOTES:
            e = get_quotes(response)
            if e is None:
                continue
            quotes += e

    with open('likes.json', 'w', encoding='utf-8') as f:
        json.dump(distinct_objects(likes), f, ensure_ascii=False, indent=2)

    with open('retweets.json', 'w', encoding='utf-8') as f:
        json.dump(distinct_objects(retweets), f, ensure_ascii=False, indent=2)

    with open('comments.json', 'w', encoding='utf-8') as f:
        json.dump(distinct_objects(comments), f, ensure_ascii=False, indent=2)

    with open('quotes.json', 'w', encoding='utf-8') as f:
        json.dump(distinct_objects(quotes), f, ensure_ascii=False, indent=2)
    print(distinct_objects(dynamic))
    with open('dynamic.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(distinct_objects(dynamic)))

    return 0
