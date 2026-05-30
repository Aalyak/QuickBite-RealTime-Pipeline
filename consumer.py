from kafka import KafkaConsumer
import json
import sqlite3

conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT,
        customer_name TEXT,
        item TEXT,
        quantity INTEGER,
        price REAL,
        status TEXT,
        timestamp TEXT
    )
''')
conn.commit()

consumer = KafkaConsumer(
    'orders',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Consuming orders...")

for message in consumer:
    order = message.value
    cursor.execute('''
        INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        order['order_id'],
        order['customer_name'],
        order['item'],
        order['quantity'],
        order['price'],
        order['status'],
        order['timestamp']
    ))
    conn.commit()
    print(f"Saved order: {order['customer_name']} ordered {order['item']}")