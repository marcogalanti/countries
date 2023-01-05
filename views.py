from flask import request, jsonify
from countries import app

@app.route("/", methods=["GET"])
def root():
    return jsonify({'message': 'please use /countries path to invoke this API'}), 200
