import requests
import os
import logging
import json
import time

root = logging.getLogger()
root.setLevel(logging.INFO)

operations = {
    '1': ['r', 'r', 'w17', 'w20', 'r', 'r'],
    '2': ['w10', 'w13', 'r', 'r']
}

URL = os.environ.get('coordinator_url')
CLIENT_ID = str(os.environ.get('client_id'))
SLOW_START = 5

def get_acess():
    url = URL + '/request_access'
    r = requests.get(url, params={'id': CLIENT_ID})
    if r.status_code != 200:
        raise Exception('Unexpected status code')


def release_access():
    url = URL + '/release_access'
    r = requests.get(url, params={'id': CLIENT_ID})
    if r.status_code != 200:
        raise Exception('Unexpected status code')


def read():
    get_acess()
    url = URL + '/get_resource'
    r = requests.get(url, params={'id': CLIENT_ID})
    if r.status_code != 200:
        raise Exception('Unexpected status code')
    val = json.loads(r.text)
    logging.info(f"Read value: {val['value']}")
    release_access()


def write(v):
    get_acess()
    url = URL + '/change_resource'
    logging.info(f"Writing value: {v}")
    r = requests.post(url, json={'id': CLIENT_ID, 'value': v})
    if r.status_code != 200:
        raise Exception(f'Unexpected status code {r.status_code}')
    release_access()

def main():
    ops = operations[CLIENT_ID]
    for op in ops:
        if op == 'r':
            read()
        elif op.startswith('w'):
            v = op[1:]
            write(v)

if __name__ == "__main__":
    logging.info(f'Waiting {SLOW_START} seconds to start requests')
    time.sleep(SLOW_START)
    main()
