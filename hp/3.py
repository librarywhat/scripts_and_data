import os.path
import sys

import requests


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    check_name = " ".join(sys.argv[1:])

    response = requests.get("https://raw.githubusercontent.com/librarywhat/scripts_and_data/refs/heads/main/hp/check.json")
    data = response.json()

    checks = data[check_name]
    for check in checks:
        result = os.system(f"cat /etc/haproxy/haproxy.cfg | grep \"{check}\"")
        if str(result)!="0":
            sys.exit(1)

if __name__ == "__main__":
    main()
