from flask import Flask, jsonify
import time, atexit, requests, os, subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)
#app.config.from_object('syncer.config')
app.config.from_pyfile('syncer.config')

SYNCER_PORT = "5000"

def check_health():
    return { "status": True }

@app.route('/health/')
def health():
    d = check_health()
    return jsonify(d)

def get_local_dirs():
    return app.config['SYNC_DIRS']

# List dirs to sync
def list_dirs():
    return { "dirs": get_local_dirs() }

def list_nodes():
    return app.config['NODES']

@app.route('/sync_dirs/')
def dirs():
    return jsonify(list_dirs())

@app.route('/dirs/')
def list_dirs():
    return ""

def get_remote_dirs(node):
    url = "http://{}:{}/sync_dirs/".format(node, SYNCER_PORT)
    res = requests.get(url)
    if res.status_code == 200:
      return res.json
    else:
      print("Could not list dirs of node {}".format(node))
      return []

def ping_node(node):
    url = "http://{}:{}/health/".format(node, SYNCER_PORT)
    res = requests.get(url)
    if res.status_code == 200:
      return True
    else:
      print("Could not contact node {}.".format(node))
      return False

def get_remote_file_metadata(path):
    print("get_remote_file_metadata")

def get_file_metadata(path):
      stat = os.stat(path)
      # seconds since epoch
      last_changed = stat.st_mtime
      return {
               "last_changed": last_changed,
               "path": path
             }

def sync_directory(directory):
    print("Syncing directory '{}'".format(directory))
    for file in os.listdir(directory):
      print("local file: {}".format(file))
      path = directory + file
      metadata = get_file_metadata(path)
      print("Metadata: {}".format(metadata))
      remote_file_info = get_remote_file_metadata(path)

def sync_node(node):
    print("Checking for node connectivity to: " + node)
    if ping_node(node):
      print("Starting sync of node: " + node)
      remote_dirs = get_remote_dirs(node)
      local_dirs = get_local_dirs()
      for dir in local_dirs:
        sync_directory(dir)

def sync_nodes():
    print("")
    print("Starting sync job.")
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

    nodes = list_nodes()
    for node in nodes:
        sync_node(node)

def start_job():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=sync_nodes,
        trigger=IntervalTrigger(seconds=5),
        id='sync_job',
        name='File sync job',
        replace_existing=True)

    atexit.register(lambda: scheduler.shutdown())

start_job()
