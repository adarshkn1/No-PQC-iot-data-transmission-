import pika
import json
import sys
import time

HOST = 'localhost'
PORT = 5672
QUEUE_NAME = 'random_data_queue'

def main():
    print(f"[*] Connecting to RabbitMQ at {HOST}:{PORT}...")
    
    # Retry connection in case container is still starting up
    connection = None
    for attempt in range(1, 6):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=HOST, port=PORT)
            )
            print("[+] Connected to RabbitMQ successfully!")
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[-] Connection attempt {attempt}/5 failed. Retrying in 2 seconds...")
            time.sleep(2)

    if not connection:
        print("[-] Could not connect to RabbitMQ. Ensure Docker container is running.")
        sys.exit(1)

    channel = connection.channel()
    
    # Declare the queue (will create if it does not exist)
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        try:
            # Decode raw bytes to UTF-8 text and parse JSON if applicable
            raw_text = body.decode('utf-8')
            parsed_data = json.loads(raw_text)
            print("\n" + "=" * 60)
            print(f"[RECEIVED] Message Tag: {method.delivery_tag}")
            print(f"[RAW PAYLOAD] {raw_text}")
            print(f"[PARSED JSON] {json.dumps(parsed_data, indent=2)}")
            print("=" * 60)
        except Exception as e:
            print(f"\n[RECEIVED RAW BYTES] {body}")

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    print(f"[*] Server listening for messages on queue: '{QUEUE_NAME}'")
    print("[*] Press Ctrl+C to exit.")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
        connection.close()
        print("[+] Connection closed.")

if __name__ == '__main__':
    main()
