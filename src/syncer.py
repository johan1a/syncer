from flask import Flask, jsonify, abort, Response, request, send_from_directory
import requests, os, logging
import sync_service

app = Flask(__name__)
app.config.from_pyfile('syncer.config')

def check_health():
  return { "status": True }

@app.route('/health/')
def health():
  return jsonify(check_health())

@app.route('/files/', methods = ["GET", "POST"])
def files():
  path = request.args.get("path")
  if request.method == "GET":
    logging.warning("Sending file: " + path)
    path = path.replace(sync_service.BASE_SYNC_DIR + "/", "")
    return send_from_directory(sync_service.BASE_SYNC_DIR, path, as_attachment=True)
  elif request.method == 'POST':
    logging.warning("Saving file: " + path)
    if request.args.get("type") == "directory":
      sync_service.create_directory(path)
      return Response(status=200)

    data = request.data
    if data:
      if sync_service.save_file(path, data):
        return Response(status=200)
    else:
      abort(400)
    abort(500)

@app.route('/metadata/')
def metadata():
  path = request.args.get("path")
  metadata = sync_service.get_file_metadata(path)
  if metadata:
    return jsonify(metadata)
  else:
    abort(404)

if __name__ == "__main__":
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    nodes = os.getenv('SYNCER_HOSTS').split(",")
    sync_service.start_job(nodes)

    app.run(debug=True, host='0.0.0.0')

