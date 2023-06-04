import json
from typing import Optional, List, Any

from ._types import RequestType


def get_type_by_url(url: str) -> Optional[RequestType]:
    for t in RequestType:
        if t.value in url:
            return t
    return None

def insert_user_action(user_actions: dict[str, set[str]], user: str, action: str):
    if not user in user_actions:
        user_actions[user] = set()
    user_actions[user].add(action)

def get_favorite_users(response: dict, user_actions: dict[str, set[str]]):
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
    for entry in entries:
        try:
            legacy = entry['content']['itemContent']['user_results']['result']['legacy']
        except KeyError:
            continue
        entry_rt.append(entry)
        insert_user_action(user_actions, legacy['screen_name'], '喜欢')
    return entry_rt


def get_retweeters(response: dict, user_actions: dict[str, set[str]]):
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
    for entry in entries:
        try:
            legacy = entry['content']['itemContent']['user_results']['result']['legacy']
        except KeyError:
            continue
        entry_rt.append(entry)
        insert_user_action(user_actions, legacy['screen_name'], '转推')
    # FIXME: seems to have bugs
    return entry_rt


def get_comments(response: dict, user_actions: dict[str, set[str]]):
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
        insert_user_action(user_actions, legacy['screen_name'], '评论')
    return entry_rt


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
            # TODO: 引用了推文
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

def compute_dynamic_list(user_actions: dict[str, set[str]]) -> List[str]:
    dynamic = []
    for user, actions in user_actions.items():
        dynamic.append(f'@{user} {" ".join(actions)}')
    dynamic.sort()
    return dynamic

def dumper(path: str) -> int:
    likes: List[dict] = []
    retweets: List[dict] = []
    comments: List[dict] = []
    quotes: List[dict] = []

    dynamic: dict[str, str[str]] = {}

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
            rt = get_favorite_users(response, dynamic)
            if rt is None:
                continue
            likes.extend(rt)
        elif req_type == RequestType.RETWEETERS:
            rt = get_retweeters(response, dynamic)
            if rt is None:
                continue
            retweets.append(rt)
        elif req_type == RequestType.COMMENT:
            rt = get_comments(response, dynamic)
            if rt is None:
                continue
            comments.append(rt)
        elif req_type == RequestType.QUOTES:
            rt = get_quotes(response)
            if rt is None:
                continue
            quotes.append(rt)
    likes = distinct_objects(likes)
    retweets = distinct_objects(retweets)
    comments = distinct_objects(comments)
    quotes = distinct_objects(quotes)

    dynamic = compute_dynamic_list(dynamic)

    with open('likes.json', 'w', encoding='utf-8') as f:
        json.dump(likes, f, ensure_ascii=False, indent=2)

    with open('retweets.json', 'w', encoding='utf-8') as f:
        json.dump(retweets, f, ensure_ascii=False, indent=2)

    with open('comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    with open('quotes.json', 'w', encoding='utf-8') as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)
    with open('dynamic.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(distinct_objects(dynamic)))

    return 0
