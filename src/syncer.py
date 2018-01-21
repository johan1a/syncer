from flask import Flask, jsonify
import time, atexit, requests, os, subprocess, logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


app = Flask(__name__)
app.config.from_pyfile('syncer.config')


SYNCER_PORT = "5000"

def check_health():
  return { "status": True }

@app.route('/health/')
def health():
  d = check_health()
  return jsonify(d)

def get_sync_dir():
  return "/sync/"

def list_nodes():
  return app.config['NODES']

def get_remote_dirs(node):
  url = "http://{}:{}/sync_dirs/".format(node, SYNCER_PORT)
  res = requests.get(url)
  if res.status_code == 200:
    return res.json
  else:
    logging.warning("Could not list dirs of node {}".format(node))
    return []

def ping_node(node):
  url = "http://{}:{}/health/".format(node, SYNCER_PORT)
  res = requests.get(url)
  if res.status_code == 200:
    return True
  else:
    logging.warning("Could not contact node {}.".format(node))
    return False

def get_remote_file_metadata(path):
  logging.warning("get_remote_file_metadata")

def get_file_type(path):
  if os.path.isdir(path):
    return "directory"
  else:
    return "file"

def get_file_metadata(path):
  stat = os.stat(path)
  # seconds since epoch
  last_changed = stat.st_mtime
  logging.info(stat)
  return {
      "last_changed": last_changed,
      "path": path,
      "type": get_file_type(path)
      }

def get_directory_metadata(directory):
  metadata = {
      "path": directory,
      "type": "directory",
      "files": []
      }
  for file in os.listdir(directory):
    path = directory + file
    metadata["files"].append(get_file_metadata(path))
  return metadata

def sync_file(file):
  path = file["path"]
  logging.warning("local file: {}".format(path))
  #remote_file_info = get_remote_file_metadata(path)

def sync_directory(directory):
  logging.warning("Syncing directory '{}'".format(directory))
  dir_metadata = get_directory_metadata(directory)
  logging.warning("metadata")
  logging.warning(dir_metadata)

  if dir_metadata and dir_metadata["files"]:
    for file in dir_metadata["files"]:
      sync_file(file)
  else:
    logging.warning("No metadata found")

def sync_node(node):
  logging.warning("Checking for node connectivity to: " + node)
  if ping_node(node):
    logging.warning("Starting sync of node: " + node)
    local_dir = get_sync_dir()
    sync_directory(local_dir)

def sync_nodes():
  logging.warning("")
  logging.warning("Starting sync job.")
  logging.warning(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

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
    logging.warning("added job to scheduler")

if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    logging.warning(root_logger)
    logging.warning("in main")
    start_job()
    app.run(debug=True, host='0.0.0.0')

