from flask import Flask, jsonify
import time, atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)
#app.config.from_object('syncer.config')
app.config.from_pyfile('syncer.config')

def check_health():
    return { "status": True }

@app.route('/health')
def health():
    d = check_health()
    return jsonify(d)

# List dirs to sync
def list_dirs():
    dirs = ["~/sync/"]
    return { "dirs": dirs }

def list_nodes():
    return app.config['NODES']

@app.route('/dirs')
def dirs():
    return jsonify(list_dirs())

def sync_nodes():
    print("")
    print("Starting sync job.")
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

    nodes = list_nodes()
    for node in nodes:
        print("Starting sync of node: " + node)

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
