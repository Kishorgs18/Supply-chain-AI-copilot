import os
import json
import time
import random
from datetime import datetime

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PRODUCTS = [
    {"id": "P001", "name": "Ergonomic Office Chair", "category": "Furniture", "price": 189.99},
    {"id": "P002", "name": "Wireless Mechanical Keyboard", "category": "Electronics", "price": 89.50},
    {"id": "P003", "name": "UltraWide Monitor 34\"", "category": "Electronics", "price": 349.99},
    {"id": "P004", "name": "Running Shoes v2", "category": "Apparel", "price": 120.00},
    {"id": "P005", "name": "Eco-Friendly Water Bottle", "category": "Home Goods", "price": 25.00}
]

COUNTRIES = ["US", "UK", "DE", "FR", "JP", "CA", "AU"]
STATUSES = ["processing", "shipped", "delayed", "delivered"]
LOG_SEVERITIES = ["INFO", "WARN", "CRITICAL"]

INCIDENT_MESSAGES = [
    "Forklift battery failure in Aisle 4 causing minor picking delays.",
    "High congestion detected at Dock 2 during inbound offloading.",
    "System update initiated on conveyor sorting unit B.",
    "Routine inventory cycle count completed successfully.",
    "Minor conveyor belt slippage detected. Maintenance team notified.",
    "Severe weather advisory delaying incoming long-haul freight arrivals."
]

CLICK_ACTIONS = ["view_item", "add_to_cart", "remove_from_cart", "checkout_click"]

def generate_transaction():
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 3)
    status = random.choice(STATUSES)
    return {
        "event_type": "transaction",
        "order_id": f"ORD-{random.randint(100000, 999999)}",
        "customer_id": f"CUST-{random.randint(1000, 9999)}",
        "product_id": product["id"],
        "category": product["category"],
        "quantity": quantity,
        "total_amount": round(product["price"] * quantity, 2),
        "destination_country": random.choice(COUNTRIES),
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_warehouse_log():
    severity = random.choice(LOG_SEVERITIES)
    # Match context: higher severity usually means actual issues
    message = random.choice(INCIDENT_MESSAGES) if severity in ["WARN", "CRITICAL"] else "Normal operations checkpoint."
    return {
        "event_type": "warehouse_log",
        "log_id": f"LOG-{random.randint(100000, 999999)}",
        "warehouse_id": f"WH-{random.choice(['CHI', 'LA', 'NY', 'LON', 'BER'])}",
        "severity": severity,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_clickstream():
    product = random.choice(PRODUCTS)
    return {
        "event_type": "clickstream",
        "session_id": f"SESS-{random.randint(1000000, 9999999)}",
        "user_id": f"USER-{random.randint(1000, 9999)}",
        "action": random.choice(CLICK_ACTIONS),
        "product_id": product["id"],
        "timestamp": datetime.utcnow().isoformat()
    }

def write_event(event):
    # Append events to a daily log file mimicking a real-time event stream landing zone
    filename = f"stream_{datetime.utcnow().strftime('%Y%m%d')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "a") as f:
        f.write(json.dumps(event) + "\n")

if __name__ == "__main__":
    print(f"🚀 Starting Real-Time Supply Chain Simulator...")
    print(f"📦 Data streaming into: {OUTPUT_DIR}")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Randomly pick which event type occurs
            roll = random.random()
            if roll < 0.60:    # 60% chance for consumer clicks
                event = generate_clickstream()
            elif roll < 0.90:  # 30% chance for product transactions
                event = generate_transaction()
            else:              # 10% chance for facility operational logs
                event = generate_warehouse_log()
                
            write_event(event)
            print(f"[{event['timestamp']}] Generated {event['event_type'].upper()}: {json.dumps(event)[:80]}...")
            
            # Sleep slightly to simulate real-time ingestion velocity
            time.sleep(random.uniform(0.2, 1.0))
            
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped gracefully.")