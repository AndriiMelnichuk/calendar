import pika
import json
from googleHelper import add_event, is_at_google, delete_event


def process_message(ch, method, properties, body):
    
    message = json.loads(body)
    # print(f"[x] Received message: {message}")
    response = {}
    access_token = message['access_token']
    if message['type'] == 'get_all_assigned_tasks':
        response = {
            # TODO  Добавить генерацию и запрос к сервису.
        }
    elif message['type'] == 'add_event_to_calendar':
        print('INFO: add task')
        add_event(message, access_token)
    elif message['type'] == 'is_event_at_calendar':
        print('INFO: is task in calendar')
        response = is_at_google(message, access_token)
    elif message['type'] == 'delete_task':
        print('INFO: delete task')
        delete_event(message, access_token)


    
    if properties.reply_to:
        response_queue = properties.reply_to
        correlation_id = properties.correlation_id
        # Відправка відповіді на чергу
        ch.basic_publish(
            exchange='',
            routing_key=response_queue,
            properties=pika.BasicProperties(
                reply_to=properties.reply_to,
                correlation_id=correlation_id
            ),
            body=json.dumps(response)
        )
        print(f"[*] Sent response: {response}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer(queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            'rabbitmq',
            # 'localhost',
            5672,   # RabbitMQ port
            '/',    # Virtual host
            pika.PlainCredentials('admin', 'password')
        )
    )
    channel = connection.channel()
    
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=process_message)
    print(f"[*] Waiting for messages in {queue_name}")
    channel.start_consuming()
