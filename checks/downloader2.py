import os
import sys

if __name__ == '__main__':
    url = "https://raw.githubusercontent.com/librarywhat/scripts_and_data/refs/heads/main/checks/"
    KEY = sys.argv[1]
    filename = KEY.split('/')[-1]

    os.system(f'wget -O {filename} {url}{KEY}')
