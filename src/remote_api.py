import requests, logging

SYNCER_PORT = "5000"

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
  logging.warning("Sending file {} to node {}".format(path, node))
  url = "http://{}:{}/files/".format(node, SYNCER_PORT)
  params = {
             "path": path,
             "type": "file"
           }
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

def create_remote_directory(node, file):
  path = file["path"]
  logging.warning("Creating directory {} on node {}".format(path, node))
  url = "http://{}:{}/files/".format(node, SYNCER_PORT)
  params = {
             "path": path,
             "type": "directory"
           }
  res = requests.post(url,
                      params = params,
                      headers={'Content-Type': 'application/octet-stream'})
  if res.status_code == 200:
    return True
  else:
    logging.warning("Could not send file {} to node {}.".format(path, node))
  return False

def retrieve_file(node, file):
  path = file["path"]
  logging.warning("Retrieving file {} from node {}".format(path, node))
  url = "http://{}:{}/files/".format(node, SYNCER_PORT)
  path = file["path"]
  params = { "path": path }
  res = requests.get(url, params = params)
  if res.status_code == 200:
    with open(path, 'wb') as f:
      f.write(res.content)
  else:
    logging.warning("Could not retrieve file {} to node {}. Got status {}".format(path, node, res.status_code))
