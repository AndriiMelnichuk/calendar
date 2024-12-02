import pika
import json
import uuid

class RpcClient(object):
    def __init__(self, host='rabbitmq', port=5672, vhost='/', user='admin', password='password'):
        # host = 'localhost'
        # Подключаемся к RabbitMQ
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host,
                port,
                vhost,
                pika.PlainCredentials(user, password),                
            )
        )
        self.channel = self.connection.channel()

        # Создаем уникальную очередь для получения ответа
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        # Настроим получение ответа
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = body

    def call(self, msg, queue_name):
        """Отправляет запрос в очередь и ждет ответа."""
        try:
            self.response = None
            self.corr_id = str(uuid.uuid4())  # Уникальный ID для отслеживания ответа
            
            # Проверяем и сериализуем сообщение
            if isinstance(msg, dict):
                msg = json.dumps(msg)
            elif not isinstance(msg, (str, bytes)):
                raise ValueError("Message must be a string, bytes, or a dictionary.")
            
            # Преобразуем строку в байты (если не байты)
            if isinstance(msg, str):
                msg = msg.encode('utf-8')
            
            # Публикуем сообщение в очередь
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id
                ),
                body=msg
            )
            print(f'[x] message send: {msg}')

            # Ожидаем ответа
            while self.response is None:
                self.connection.process_data_events()  # Обрабатываем события
            
            return json.loads(self.response.decode('utf-8'))  # Возвращаем ответ как строку
        
        except Exception as e:
            print(f"Error occurred while sending message: {e}")
            return None

