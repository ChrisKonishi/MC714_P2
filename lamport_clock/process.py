import logging
import os
import requests
import time
import threading
from flask import Flask, Response, request

class Clock():
    def __init__(self):
        self.value = 0
        self.id = int(os.environ.get('my_id'))
        self.start_clock()

    def start_clock(self):
        self.value += self.id
        threading.Timer(1.0, self.start_clock).start()

clock = Clock()

app = Flask(__name__)
root = logging.getLogger()
root.setLevel(logging.INFO)

def send_msg(content, id, ts):
    url = f'http://process{id}:5000/receive_msg'
    r = requests.post(url=url, params={'ts':ts, 'content':content})
    return r

@app.route("/receive_msg", methods=['POST'])
def receive_msg():
    global clock
    now = clock.value
    ts = int(request.args.get('ts'))
    if ts >= now:
        clock.value = ts + 1
        logging.info(f'Process {clock.id} adjusted clock from {now} to {ts + 1}')
    else:
        logging.info(f'Process {clock.id} received message with timestamp {ts}, local time is {now}')
    time.sleep(2)
    content = request.args.get('content')
    if len(content) > 1:
        next = content[1]
        ts = clock.value
        logging.info(f'Process {clock.id} sending message with timestamp {ts} to process {next}')
        r = send_msg(content[1:], next, ts)
        if r.status_code != 200:
            logging.info('Task error')
    else:
        logging.info('Finishing tasks')
        url = f'http://application:5000/receive_answer'
        requests.post(url=url)
    return Response(), 200

