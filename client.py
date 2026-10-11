import pika
import json
import random
import time
import uuid
import sys

HOST = 'localhost'
PORT = 5672
QUEUE_NAME = 'random_data_queue'

def generate_random_data():
    """Generates dynamic random sample telemetry data."""
    data_types = ['TELEMETRY', 'SENSOR_READING', 'USER_ACTIVITY', 'SYSTEM_METRIC']
    selected_type = random.choice(data_types)
    
    payload = {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event_type": selected_type,
        "device_id": f"DEV-{random.randint(1000, 9999)}",
        "metrics": {
            "temperature_celsius": round(random.uniform(18.0, 85.0), 2),
            "humidity_percent": round(random.uniform(30.0, 90.0), 2),
            "cpu_load_percent": round(random.uniform(5.0, 99.9), 1),
            "memory_usage_mb": random.randint(512, 16384),
            "random_hash": hex(random.getrandbits(64))[2:]
        },
        "raw_text_payload": f"Random string content: {random.choice(['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'OMEGA'])} - value {random.randint(100, 999)}"
    }
    return payload

def main():
    # Number of messages to send; pass 'continuous' or integer argument if desired
    msg_count = float('inf')
    interval = 1.5

    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            msg_count = int(sys.argv[1])
        elif sys.argv[1].lower() == 'continuous':
            msg_count = float('inf')

    print(f"[*] Connecting to RabbitMQ at {HOST}:{PORT}...")
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=HOST, port=PORT)
        )
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[-] Could not connect to RabbitMQ at {HOST}:{PORT}.")
        print("[-] Ensure the Docker container is running (`docker compose up -d`).")
        sys.exit(1)

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    print(f"[+] Connected! Sending random data messages to queue '{QUEUE_NAME}'...")
    print(f"[*] Interval: {interval}s | Target Count: {'Infinite (Continuous)' if msg_count == float('inf') else msg_count}")
    print("[*] Press Ctrl+C to stop.\n")

    sent = 0
    try:
        while sent < msg_count:
            sent += 1
            data = generate_random_data()
            json_payload = json.dumps(data)

            # Publish message using basic_publish to default exchange
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json_payload,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=2  # make message persistent
                )
            )

            print(f"[SENT #{sent}] ID: {data['event_id']} | Type: {data['event_type']} | Payload Size: {len(json_payload)} bytes")
            print(f"   --> Content: {json_payload[:120]}...")
            
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[*] Stopped by user.")
    finally:
        connection.close()
        print(f"[+] Finished sending {sent} messages. Connection closed.")

if __name__ == '__main__':
    main()
