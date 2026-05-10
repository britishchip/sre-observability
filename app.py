from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

@app.route('/')
def index():
    start = time.time()
    # randomly simulate occasional slowness
    time.sleep(random.uniform(0, 0.5))
    status = random.choices([200, 500], weights=[95, 5])[0]
    REQUEST_COUNT.labels('GET', '/', status).inc()
    REQUEST_LATENCY.labels('/').observe(time.time() - start)
    if status == 500:
        return jsonify({"error": "something went wrong"}), 500
    return jsonify({"status": "ok"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
