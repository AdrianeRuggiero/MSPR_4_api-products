import json
import pika
from app.config import settings

def get_channel():
    connection_params = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='product_created', durable=True)
    return channel

# Publier un message
def publish_product_created(product_data: dict, channel=None):
    if channel is None:
        channel = get_channel()
    channel.basic_publish(
        exchange='',
        routing_key='product_created',
        body=json.dumps(product_data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    channel.close()

# Consommateur (à exécuter manuellement)
def consume_product_created(callback):
    channel = get_channel()

    def wrapper(ch, method, properties, body):
        data = json.loads(body)
        callback(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='product_created', on_message_callback=wrapper)
    print(" [*] En attente de messages sur 'product_created'. CTRL+C pour arrêter.")
    channel.start_consuming()
