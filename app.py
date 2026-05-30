from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from kafka import KafkaProducer
import sqlite3
import json
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def get_db():
    conn = sqlite3.connect('orders.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/restaurant')
def restaurant():
    return render_template('producer.html')

@app.route('/api/orders')
def get_orders():
    conn = get_db()
    orders = conn.execute('SELECT * FROM orders ORDER BY timestamp DESC LIMIT 50').fetchall()
    return jsonify([dict(order) for order in orders])

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
    revenue = conn.execute('SELECT SUM(price*quantity) as total FROM orders').fetchone()['total']
    popular = conn.execute('SELECT item, COUNT(*) as count FROM orders GROUP BY item ORDER BY count DESC LIMIT 1').fetchone()
    return jsonify({
        'total_orders': total,
        'total_revenue': round(revenue or 0, 2),
        'popular_item': popular['item'] if popular else 'N/A'
    })

@app.route('/api/place_order', methods=['POST'])
def place_order():
    data = request.get_json()
    order = {
        'order_id': str(uuid.uuid4()),
        'customer_name': data['name'],
        'item': data['item'],
        'quantity': int(data['quantity']),
        'price': float(data['price']),
        'status': 'placed',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    producer.send('orders', value=order)
    return jsonify({'message': 'Order placed!'}), 200

@app.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    conn = get_db()
    conn.execute('UPDATE orders SET status = ? WHERE order_id = ?',
                 (data['status'], data['order_id']))
    conn.commit()
    return jsonify({'message': 'Status updated!'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)