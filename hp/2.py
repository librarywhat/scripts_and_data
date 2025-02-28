import json
import os.path
import sys

import requests


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    check_name = " ".join(sys.argv[1:])
    path = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(path, 'checks.json'), 'r',encoding="utf-8") as f:
        data:dict=json.loads(f.read())

    checks = data[check_name]
    for check in checks:
        result = os.system(f"cat /etc/haproxy/haproxy.cfg | grep \"{check}\"")
        if str(result)!="0":
            sys.exit(1)

if __name__ == "__main__":
    main()
