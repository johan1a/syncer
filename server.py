from flask import jsonify
from flask import Flask
app = Flask(__name__)

def check_health():
    return { "status": True }

@app.route('/health')
def health():
    d = check_health()
    return jsonify(d)
