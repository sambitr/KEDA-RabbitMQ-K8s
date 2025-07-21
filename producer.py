import pika
import time

# --- RabbitMQ Connection Info ---
RABBITMQ_HOST = 'localhost'         # or use 'rabbitmq' if running inside k8s
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guestpassword'
QUEUE_NAME = 'task-queue'

# --- Create Connection Parameters ---
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)

# --- Connect to RabbitMQ ---
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# --- Declare Queue (durable) ---
channel.queue_declare(queue=QUEUE_NAME, durable=True)

# --- Send Messages ---
message_count = 500
for i in range(message_count):
    body = f"Message #{i}"
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
    )
    print(f"[x] Sent: {body}")
    time.sleep(0.1)

# --- Close Connection ---
connection.close()
print("All messages sent.")
