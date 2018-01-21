from flask import Flask, jsonify, abort, Response, request, send_from_directory
import time, atexit, requests, os, subprocess, logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


app = Flask(__name__)
app.config.from_pyfile('syncer.config')


SYNCER_PORT = "5000"
BASE_SYNC_DIR = "/sync/"

def check_health():
  return { "status": True }

def get_sync_base_dir():
  return get_file_metadata(BASE_SYNC_DIR)

def list_nodes():
  return app.config['NODES']

def get_remote_file_metadata(node, path):
  url = "http://{}:{}/metadata/".format(node, SYNCER_PORT)
  params = { "path": path }
  res = requests.get(url, params = params)
  return res

def ping_node(node):
  url = "http://{}:{}/health/".format(node, SYNCER_PORT)
  res = requests.get(url)
  if res.status_code == 200:
    return True
  else:
    logging.warning("Could not contact node {}.".format(node))
    return False

def send_file(node, file):
  path = file["path"]
  print("Sending file {} to node {}".format(path, node))
  url = "http://{}:{}/files/".format(node, SYNCER_PORT)
  params = { "path": path }
  with open(path, 'rb') as f:
    data = f.read()
    res = requests.post(url,
                        data = data,
                        params = params,
                        headers={'Content-Type': 'application/octet-stream'})
    if res.status_code == 200:
      return True
    else:
      logging.warning("Could not send file {} to node {}.".format(path, node))
  return False

def retrieve_file(node, file):
  path = file["path"]
  print("Retrieving file {} from node {}".format(path, node))
  url = "http://{}:{}/files/".format(node, SYNCER_PORT)
  path = file["path"]
  params = { "path": path }
  res = requests.get(url, params = params)
  if res.status_code == 200:
    with open(path) as f:
      f.write(res.content)
  else:
    logging.warning("Could not retrieve file {} to node {}. Got status {}".format(path, node, res.status_code))

def get_file_type(path):
  if os.path.isdir(path):
    return "directory"
  else:
    return "file"

def save_file(path, data):
  with open(path) as file:
    file.write(data)
    return True
  return False

def get_file_metadata(path):
  if not os.path.exists(path):
    return None

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

def is_newer(local, remote):
  return local["last_changed"] < remote["last_changed"]

def sync_data(node, file):
  path = file["path"]
  response = get_remote_file_metadata(node, path)
  if response.status_code == 200:
    remote_file = response.json
    if is_newer(file, remote_file):
      send_file(node, file)
    else:
      retrieve_file(node, file)
  elif response.status_code == 404:
    logging.warning("File {} could not be found on node {}".format(path, node))
    send_file(node, file)

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

@app.route('/files/', methods = ["GET", "POST"])
def files():
  if request.method == "GET":
    logging.warning("Sending file: " + path)
    path = request.args.get("path").replace(BASE_SYNC_DIR, "")
    return send_from_directory(BASE_SYNC_DIR, path, as_attachment=True)
  elif request.method == 'POST':
    data = request.form
    if save_file(path, data):
      return Response(status=200)
    else:
      abort(500)

@app.route('/metadata/<path>/')
def metadata():
  path = request.args.get("path")
  metadata = get_file_metadata("/" + path)
  if metadata:
    return jsonify(metadata)
  else:
    abort(404)

if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    logging.warning(root_logger)
    logging.warning("in main")
    start_job()
    app.run(debug=True, host='0.0.0.0')

