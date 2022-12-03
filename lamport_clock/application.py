import requests
import logging
from flask import Flask, Response
from threading import Thread

root = logging.getLogger()
root.setLevel(logging.INFO)

app = Flask(__name__)

@app.route("/receive_answer", methods=['POST'])
def receive_answer():
    logging.info('Task done')
    return Response(), 200

def send_task(content):
    logging.info('Starting task')
    url = f'http://process{content[0]}:5000/receive_msg'
    requests.post(url=url, params={'ts':1, 'content':content})

thread = Thread(target=send_task, args=('2132121',))
thread.start()