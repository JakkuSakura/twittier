import random
from typing import List


def draw(path: str, pools: List[int], requires: List[str]):

    comments = set()
    retweets = set()
    likes = set()
    quotes = set()

    with open(path, 'r', encoding='utf-8') as f:
        dynamics = f.readlines()

    for dynamic in dynamics:
        if '评论了推文' in dynamic:
            comments.add(dynamic.split()[0])
        if '转推了推文' in dynamic:
            retweets.add(dynamic.split()[0])
        if '喜欢了推文' in dynamic:
            likes.add(dynamic.split()[0])
        if '引用了推文' in dynamic:
            quotes.add(dynamic.split()[0])

    retweets = retweets | quotes

    if len(requires) == 0:
        requires = ['comment', 'retweet', 'like']

    users = comments | retweets | likes
    for require in requires:
        if require == 'comment':
            users = users & comments
        elif require == 'retweet':
            users = users & retweets
        elif require == 'like':
            users = users & likes
        else:
            print('Unknown require: ' + require)
            return

    print('Total users: ' + str(len(users)))
    for i, user in enumerate(users):
        print(f'{user:<18}', end='') if i % 5 != 4 else print(f'{user:<18}')
    print('\n\n')

    for pool, count in enumerate(pools):
        print(f'====== Pool: {pool + 1} Start ======')
        user_sample = random.sample(users, count)
        for i, user in enumerate(user_sample):
            print(f'{user:<18}', end='') if i % 5 != 4 else print(f'{user:<18}')
        if len(user_sample) % 5 != 0:
            print('')

        users = users - set(user_sample)

        print(f'====== Pool: {pool + 1} End ======\n\n')


