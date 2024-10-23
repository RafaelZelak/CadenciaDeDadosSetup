# -*- coding: UTF-8 -*-
# author: dameng
#

"""
cc,dd 文字<->彩色文字转换
"""
import re
import sys
from termcc.unicodes_codec import TERMCC_UNICODE, TERMCC_UNICODE_REVERSE_KV

__all__ = ['cc', 'dd', 'get_termcc_regexp']

PY2 = sys.version_info[0] is 2

_TERMCC_REGEXP = None
_DEFAULT_LEFT_DELIMITER = ":"
_DEFAULT_RIGHT_DELIMITER = ":"


def cc(string, delimiters=(_DEFAULT_LEFT_DELIMITER, _DEFAULT_RIGHT_DELIMITER)):
    """
    转换带有语义的字符为带有颜色的字符

    :param string:  输入的字符
    :param delimiters:   控制字符转换
    """
    pattern = re.compile(u'%s([a-zA-Z0-9\+\-_&.ô’Åéãíç()!#*]+)%s' % delimiters)
    def replace(match):
        mg = match.group(1)
        return TERMCC_UNICODE.get(mg, mg)
    return pattern.sub(replace, string)


def dd(string, delimiters=(_DEFAULT_LEFT_DELIMITER, _DEFAULT_RIGHT_DELIMITER)):
    """
    将输出的字符串逆向转换成原始字符串

    :param string:  输入的字符
    :param delimiters:   控制字符转换
    """
    def replace(match):
        val = TERMCC_UNICODE_REVERSE_KV.get(match.group(0), match.group(0))
        return delimiters[0] + val + delimiters[1]
    return get_termcc_regexp().sub(replace, string)


def get_termcc_regexp():
    global _TERMCC_REGEXP
    if _TERMCC_REGEXP is None:
        pattern = u'(' + u'|'.join(re.escape(u) for u in TERMCC_UNICODE.values()) + u')'
        _TERMCC_REGEXP = re.compile(pattern)
    return _TERMCC_REGEXP


def clean(string, delimiters=(_DEFAULT_LEFT_DELIMITER, _DEFAULT_RIGHT_DELIMITER)):
    return re.sub(delimiters[0]+'.*'+delimiters[1], '', string)

def show():
    import argparse
    parser = argparse.ArgumentParser(description='example: '+ cc(":green: hello:reset::world_map:"))
    parser.add_argument('--left-delimiter', default=':', help='the left delimeter')
    parser.add_argument('--right-delimiter', default=':', help='the right delimeter')
    parser.add_argument('text',  help=':green: hello world :reset: :world_map:')
    args = parser.parse_args()
    text = cc(args.text, delimiters=(args.left_delimiter, args.right_delimiter))
    print(text)

if __name__ == '__main__':
    show()
