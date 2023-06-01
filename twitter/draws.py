import argparse
import os
import logging
import random


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to file')
    args = parser.parse_args()

    users = []
    with open(args.path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                users.append(line)
    print('available users:', len(users))
    user_per_row = 5
    # print 5 users per row
    for i in range(0, len(users), user_per_row):
        print('\t'.join(users[i:i + user_per_row]))

    draw_list = [
        ('first award', 3),
        ('second award', 9),
        ('third award', 15),
    ]
    for award, num in draw_list:
        print('********drawing %s********' % award)
        user_sample = random.sample(users, num)
        print('\t'.join(user_sample))
        print('********drawing %s complete********' % award)
        for lucky_user in user_sample:
            users.remove(lucky_user)
    print('drawing complete')


if __name__ == '__main__':
    main()
