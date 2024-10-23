import sys
from termcc.unicodes_codec import TERMCC_UNICODE
import json

def query():
    result = {}
    conditions = sys.argv[1:]
    for key in TERMCC_UNICODE.keys():
        for cond in conditions:
            if cond in key:
                result[key] = TERMCC_UNICODE[key]
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    query()