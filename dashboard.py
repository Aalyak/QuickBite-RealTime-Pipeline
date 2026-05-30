import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('orders.db')

df = pd.read_sql_query("SELECT * FROM orders", conn)

print(f"Total orders: {len(df)}")
print(df.head())

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Realtime Order Pipeline Dashboard', fontsize=16)

# orders by item
item_counts = df['item'].value_counts()
axes[0,0].bar(item_counts.index, item_counts.values, color='orange')
axes[0,0].set_title('Orders by Item')
axes[0,0].set_xlabel('Item')
axes[0,0].set_ylabel('Count')

# orders by status
status_counts = df['status'].value_counts()
axes[0,1].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
axes[0,1].set_title('Order Status')

# revenue by item
df['revenue'] = df['price'] * df['quantity']
revenue_by_item = df.groupby('item')['revenue'].sum()
axes[1,0].bar(revenue_by_item.index, revenue_by_item.values, color='green')
axes[1,0].set_title('Revenue by Item')
axes[1,0].set_xlabel('Item')
axes[1,0].set_ylabel('Revenue (₹)')

# orders over time
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
orders_by_hour = df.groupby('hour').size()
axes[1,1].plot(orders_by_hour.index, orders_by_hour.values, marker='o', color='blue')
axes[1,1].set_title('Orders by Hour')
axes[1,1].set_xlabel('Hour')
axes[1,1].set_ylabel('Count')

plt.tight_layout()
plt.savefig('dashboard.png')
plt.show()
print("Dashboard saved as dashboard.png")