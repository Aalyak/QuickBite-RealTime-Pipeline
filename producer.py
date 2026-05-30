from kafka import KafkaProducer
import json
import time
from faker import Faker
import random

fake = Faker()
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def generate_order():
    return {
        'order_id': fake.uuid4(),
        'customer_name': fake.name(),
        'item': random.choice(['Pizza', 'Burger', 'Biryani', 'Pasta', 'Sandwich']),
        'quantity': random.randint(1, 5),
        'price': round(random.uniform(100, 1000), 2),
        'status': random.choice(['placed', 'preparing', 'delivered']),
        'timestamp': fake.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S')
    }

while True:
    order = generate_order()
    producer.send('orders', value=order)
    print(f"Sent order: {order}")
    time.sleep(2)