"""A deliberately small web service for Task 4.2."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return "SWE40006 Task 4.2 starter is running.\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/health")
def health():
    return jsonify(status="ok", service="starter-web", version="1.0.0")
