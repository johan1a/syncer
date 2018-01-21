from flask import Flask, jsonify
import time, atexit, requests, os, subprocess, logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


app = Flask(__name__)
app.config.from_pyfile('syncer.config')


SYNCER_PORT = "5000"

def check_health():
  return { "status": True }

def get_sync_base_dir():
  return get_file_metadata("/sync/")

def list_nodes():
  return app.config['NODES']

def get_remote_file_metadata(node, path):
  url = "http://{}:{}/files{}".format(node, SYNCER_PORT, path)
  res = requests.get(url)
  if res.status_code == 200:
    return res.json
  else:
    logging.warning("Unable to retrive metadata for {} from node {}".format(path, node))
    return {}

def ping_node(node):
  url = "http://{}:{}/health/".format(node, SYNCER_PORT)
  res = requests.get(url)
  if res.status_code == 200:
    return True
  else:
    logging.warning("Could not contact node {}.".format(node))
    return False

def get_file_type(path):
  if os.path.isdir(path):
    return "directory"
  else:
    return "file"

def get_file_metadata(path):
  stat = os.stat(path)
  # seconds since epoch
  last_changed = stat.st_mtime
  file_type = get_file_type(path)
  metadata = {
      "last_changed": last_changed,
      "path": path,
      "type": file_type
      }
  if file_type == "directory":
    metadata["files"] = []
    for file in os.listdir(path):
      metadata["files"].append(get_file_metadata(path + file))
  return metadata

def is_directory(file):
  return file["type"] == "directory"

def sync_data(node, file):
  path = file["path"]
  remote_file_info = get_remote_file_metadata(node, path)

def sync_file(node, file):
  path = file["path"]
  logging.warning("Syncing file '{}'".format(path))
  metadata = get_file_metadata(path)
  logging.warning(metadata)

  if metadata:
    if is_directory(metadata):
      for subfile in metadata["files"]:
        sync_file(node, subfile)
    else:
        sync_data(node, file)
  else:
    logging.warning("No metadata found")

def sync_node(node):
  logging.warning("Checking for node connectivity to: " + node)
  if ping_node(node):
    logging.warning("Starting sync of node: " + node)
    sync_file(node, get_sync_base_dir())

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


@app.route('/health/')
def health():
  d = check_health()
  return jsonify(d)

@app.route('/files/<path>/')
def files(path):
  return jsonify(get_file_metadata("/" + path))

if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    logging.warning(root_logger)
    logging.warning("in main")
    start_job()
    app.run(debug=True, host='0.0.0.0')

