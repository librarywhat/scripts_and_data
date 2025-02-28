import os.path
import sys

import requests


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    url = sys.argv[1]

    response = requests.get(url)
    path = os.path.abspath(os.path.dirname(__file__))
    print(os.path.join(path, 'checks.json'))
    with open(os.path.join(path, 'checks.json'), 'wb') as f:
        f.write(response.content)

if __name__ == "__main__":
    main()
