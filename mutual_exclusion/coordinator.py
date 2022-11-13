from flask import Flask, Response, jsonify, request
import threading
import time
import logging

root = logging.getLogger()
root.setLevel(logging.INFO)

app = Flask(__name__)

resourse_semaphore = threading.Semaphore(value=1)
value = 10

SLEEP_TIME = 5


@app.route("/request_access", methods=['GET'])
def get_access():
    logging.info(f"Client {request.args.get('id')} asking for access")
    resourse_semaphore.acquire()
    logging.info(f"Granting access to client {request.args.get('id')}")
    return Response(), 200


@app.route("/release_access", methods=['GET'])
def release_access():
    logging.info(f"Releasing access to client {request.args.get('id')}")
    resourse_semaphore.release()
    return Response(), 200


@app.route("/get_resource", methods=['GET'])
def get_resource():
    logging.info(f"Client {request.args.get('id')} reading resource")
    time.sleep(SLEEP_TIME)
    return jsonify(dict(value=value)), 200


@app.route("/change_resource", methods=['POST'])
def change_resource():
    global value
    v = request.json.get('value')
    logging.info(f"Client {request.json.get('id')} writing to resource {v}")
    time.sleep(SLEEP_TIME)
    if v:
        value = v
        return Response(), 200
    else:
        return Response(), 500
