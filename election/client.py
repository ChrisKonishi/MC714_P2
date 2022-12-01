from flask import Flask, Response, request, abort
import os
import threading
import time
import logging
import requests

root = logging.getLogger()
root.setLevel(logging.INFO)

SLOW_START = 2
CHECK_FREQUENCY = 3
coordinator = int(os.environ.get('initial_coordinator'))
dead_ids = []
lock = threading.Lock()
alive = True

class NextClientIsMe(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def get_url(id: int) -> str:
    return f'http://service{id}:5000'

def get_my_id():
    return int(os.environ.get('my_id'))

def get_n_clients():
    return int(os.environ.get('n_clients'))

def get_next_id(id: int) -> int:
    lock.acquire()
    n_clients = get_n_clients()
    id += 1
    if id > n_clients:
        id = 1
    while id in dead_ids:
        if id > n_clients:
            id = 1
        else:
            id += 1
    if id == get_my_id():
        lock.release()
        raise NextClientIsMe('All clients dead')
    lock.release()
    return id

def check_alive():
    logging.info(f"Starting health check in {SLOW_START} seconds")
    time.sleep(SLOW_START)

    my_id = get_my_id()

    while True:
        next_id = get_next_id(my_id)
        url = get_url(next_id) + '/health_check'
        r = requests.get(url)
        if r.status_code != 200:
            if next_id == coordinator:
                logging.info('Id {} starting new election'.format(my_id))
                requests.post(get_url(my_id) + '/start_election', json={'clients': []})
        time.sleep(CHECK_FREQUENCY)

def mark_dead_clients(alive: list):
    lock.acquire()
    for i in range(1, get_n_clients()):
        if i not in alive and i not in dead_ids:
            dead_ids.append(i)
    lock.release()

t = threading.Thread(target=check_alive)
t.start()

app = Flask(__name__)

@app.before_request
def am_i_alive():
    if alive:
        pass
    else:
        abort(500)

@app.route("/health_check", methods=['GET'])
def health_check():
    return Response(), 200

@app.route("/kill", methods=['GET'])
def kill_me():
    global alive
    logging.info(f'Id {get_my_id()} killing itself')
    alive = False
    return Response(), 200

@app.route("/start_election", methods=['POST'])
def start_election():
    global coordinator

    my_id = get_my_id()
    clients = request.json.get('clients')
    if clients is None:
        clients = []

    # finished election
    if my_id in clients:
        logging.info('Election finished, detected clients: {}'.format(clients))
        logging.info('New coordinator: {}'.format(max(clients)))
        clients = sorted(clients)
        mark_dead_clients(clients)
        next_id = get_next_id(my_id)
        url = get_url(next_id)
        coordinator = clients[-1]
        logging.info('Election finished. new coordinator: {}. Alive clients: {}'.format(clients[-1], clients))
        requests.post(url + '/inform_results', json={'clients': clients, 'coordinator': clients[-1], 'starter': my_id})

        return Response(), 200

    c_id = my_id
    clients.append(my_id)
    try:
        while True:
            next_id = get_next_id(c_id)
            url = get_url(next_id) + '/start_election'
            r = requests.post(url, json={'clients': clients})
            if r.status_code == 200:
                break
            else:
                c_id = next_id
    except NextClientIsMe:
        logging.error("Only {} alive, nothing to do".format(my_id))
    return Response(), 200

@app.route('/inform_results', methods=['POST'])
def inform_results():
    global coordinator
    my_id = get_my_id()
    clients = request.json.get('clients')
    coordinator = clients[-1]
    logging.info(f'New coordinator received: {coordinator}')
    mark_dead_clients(clients)
    next_id = get_next_id(my_id)
    if next_id == request.json.get('starter'):
        return Response(), 200  
    url = get_url(next_id)
    requests.post(url + '/inform_results', json={'clients': clients, 'coordinator': clients[-1], 'starter': request.json.get('starter')})
    return Response(), 200
