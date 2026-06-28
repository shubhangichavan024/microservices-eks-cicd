# product-service/app.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/products')
def get_products():
    return jsonify([
        {"id": 1, "name": "Laptop",  "price": 999.99},
        {"id": 2, "name": "Phone",   "price": 499.99},
    ])

@app.route('/health')
def health(): return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)