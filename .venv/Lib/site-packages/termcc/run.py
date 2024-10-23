# coding=utf8
# author: dameng

from termcc.cc import cc as termcc

def show():
    import argparse
    parser = argparse.ArgumentParser(description='example: '+termcc(":green: hello:reset::world_map:"))
    parser.add_argument('--left-delimiter', default=':', help='the left delimeter')
    parser.add_argument('--right-delimiter', default=':', help='the right delimeter')
    parser.add_argument('text',  help=':green: hello world :reset: :world_map:')
    args = parser.parse_args()
    text = termcc(args.text, delimiters=(args.left_delimiter, args.right_delimiter))
    print(text)

if __name__ == '__main__':
    show()
