import argparse
import sys

from .status_dumper import dumper


def main():
    parser = argparse.ArgumentParser(prog='twittier')
    subparser = parser.add_subparsers(title='Command', help='Available commands', dest='subparser_name')

    parser_status = subparser.add_parser('status_dumper', help='dump status from twitter http request')
    parser_status.add_argument('path', help='path to twitter .har file')

    args = parser.parse_args()

    if args.subparser_name == 'status_dumper':
        return dumper(args.path)
if __name__ == '__main__':
    sys.exit(main())
