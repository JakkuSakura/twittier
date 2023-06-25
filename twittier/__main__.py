import argparse
import sys

from .status_dumper import parse_and_dump_har_file
from .lucky_draw import draw


def main():
    parser = argparse.ArgumentParser(prog='twittier')
    subparser = parser.add_subparsers(title='Command', help='Available commands', dest='subparser_name')

    parser_status = subparser.add_parser('status_dumper', help='dump status from twitter http request')
    parser_status.add_argument('path', help='path to twitter .har file')

    parser_draw = subparser.add_parser('draw', help='lucky draw from twitter user list')
    parser_draw.add_argument('path', help='path to twitter user list')
    parser_draw.add_argument('-p', '--pool', nargs='+', type=int, help='pool of users to draw from', default=[])
    parser_draw.add_argument('-r', '--requires', nargs='+', type=str,
                             help='What kind of action is needed. (comment, retweet, like)',
                             default=['like', 'retweet', 'comment'])

    args = parser.parse_args()

    if args.subparser_name == 'status_dumper':
        return parse_and_dump_har_file(args.path)
    elif args.subparser_name == 'draw':
        if len(args.pool) == 0:
            print('twittier draw: error: the following arguments are required: -p/--pool (at least one)')
            return 1
        return draw(args.path, args.pool, args.requires)


if __name__ == '__main__':
    sys.exit(main())
