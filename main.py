import ctypes
import datetime
import os
import random
import string
import time
import urllib.request
from os import path
from threading import Thread, Lock

import requests
from bs4 import BeautifulSoup
from colorama import init, Fore

suffix = "link"
base_url = "https://ctrlv." + suffix + "/{}"
lock = Lock()
hits = 0
bad = 0
os.system("cls")
tried = []


def random_char(y: int):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=y))


def update_title():
    ctypes.windll.kernel32.SetConsoleTitleW('CTRLV Scrapper | Hits: {} | Bad: {} | Tried: {}'.format(hits, bad, len(tried)))


def load_tries():
    global tried
    file_path = 'tried' + suffix.upper() + '.txt'
    if path.exists(file_path):
        with open(file_path) as f:
            tried = f.read().split('\n');


def check_if_dir_exists():
    os.makedirs('./imgs' + suffix.upper(), exist_ok=True)


def save_tries():
    with open('tried' + suffix.upper() + '.txt', 'w') as f:
        for item in tried:
            f.write("%s\n" % item)


def download_file(url, name):
    urllib.request.urlretrieve(url, './imgs' + suffix.upper() + '/' + name)
    url_split = url.split('/')
    created_time = time.mktime(
        datetime.datetime.strptime(url_split[6] + "/" + url_split[5] + "/" + url_split[4], "%d/%m/%Y").timetuple())
    os.utime('./imgs' + suffix.upper() + '/' + name, (created_time, created_time))


def worker():
    global hits
    global bad
    global tried
    while True:
        random_string = random_char(4)
        if random_string in tried:
            update_title()
            continue
        else:
            response = requests.get(url=base_url.format(random_string))
            soup = BeautifulSoup(response.content, 'html.parser')
            src = soup.find('img', {'class': 'outline'}).attrs['src']
            if src != '/images/notexists.png':
                lock.acquire()
                print(Fore.GREEN + f'[VALID] {base_url.format(random_string)}')
                lock.release()
                hits += 1
                download_file("https://ctrlv." + suffix + src, random_string + ".png")
            else:
                lock.acquire()
                print(Fore.RED + f'[INVALID] {base_url.format(random_string)}')
                lock.release()
                bad += 1
            tried.append(random_string)
            if len(tried) % 1000 == 0:
                save_tries()
            update_title()


if __name__ == "__main__":
    update_title()
    init()
    thread_numbers = int(input("[1-100] Threads: "))
    check_if_dir_exists()
    load_tries()
    try:
        c = 0
        while c < thread_numbers:
            processThread = Thread(target=worker)
            processThread.start()
            c += 1
    except KeyboardInterrupt:
        pass
