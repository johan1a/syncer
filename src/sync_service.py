from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time, atexit, os, subprocess, logging
import remote_api
BASE_SYNC_DIR = "/sync"

def get_file_type(path):
  if os.path.isdir(path):
    return "directory"
  else:
    return "file"

def save_file(path, data):
  with open(path, "wb") as file:
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
      metadata["files"].append(get_file_metadata(path + "/" + file))
  return metadata

def create_directory(path):
  if not os.path.exists(path):
    os.makedirs(path)

def is_directory(file):
  return file["type"] == "directory"

def is_newer(local, remote):
  return local["last_changed"] < remote["last_changed"]

def same_file(local, remote):
  return local["last_changed"] == remote["last_changed"]

def sync_data(node, file):
  path = file["path"]
  response = remote_api.get_remote_file_metadata(node, path)
  if not is_directory(file) and response.status_code == 200:
    remote_file = response.json()
    if same_file(file, remote_file):
      logging.warning("{} is in sync between us and {}.".format(path, node))
    elif is_newer(file, remote_file):
      logging.warning("There is an older version of {} on {}.".format(path, node))
      remote_api.send_file(node, file)
    else:
      logging.warning("There is a newer version of {} on {}.".format(path, node))
      remote_api.retrieve_file(node, file)
  elif response.status_code == 404:
    logging.warning("File {} could not be found on node {}".format(path, node))
    if is_directory(file):
      remote_api.create_remote_directory(node, file)
    else:
      remote_api.send_file(node, file)

def sync_file(node, file):
  path = file["path"]
  logging.warning("Syncing file '{}'".format(path))
  metadata = get_file_metadata(path)
  logging.debug(metadata)

  if metadata:
    sync_data(node, file)
    if is_directory(metadata):
      for subfile in metadata["files"]:
        sync_file(node, subfile)
  else:
    logging.warning("No metadata found")

def get_sync_base_dir():
  return get_file_metadata(BASE_SYNC_DIR)

def sync_node(node):
  logging.warning("Checking for node connectivity to: " + node)
  if remote_api.ping_node(node):
    logging.warning("Starting sync of node: " + node)
    base_dir = get_sync_base_dir()
    for file in base_dir["files"]:
      sync_file(node, get_file_metadata(file["path"]))

def sync_nodes(nodes):
  logging.warning("")
  logging.warning("Starting sync job.")
  logging.warning(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

  for node in nodes:
    sync_node(node)

def start_job(nodes):
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=lambda: sync_nodes(nodes),
        trigger=IntervalTrigger(seconds=10),
        id='sync_job',
        name='File sync job',
        replace_existing=True)
    atexit.register(lambda: scheduler.shutdown())
    logging.warning("added job to scheduler")

