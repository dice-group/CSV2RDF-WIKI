import pika

class Messaging(object):
    def __init__(self):
        self.connection = self.connect_to_rabbit()
        self.channel = self.retrieve_channel(self.connection)

    def connect_to_rabbit(self):
        credentials = pika.PlainCredentials("guest","guest")
        conn_params = pika.ConnectionParameters("localhost", credentials=credentials)
        connection = pika.BlockingConnection(conn_params)
        return connection

    def retrieve_channel(self, connection):
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1) # do not send next msg before ack
        return channel

    def declare_direct_exchange(self, name):
        self.channel.exchange_declare(exchange=name,
                                      type="direct",
                                      passive=False, #will create exchange if does not exist
                                      durable=True,
                                      auto_delete=False)

    def declare_queue(self, name):
        self.channel.queue_declare(queue=name)

    def get_message_props(self):
        msg_props = pika.BasicProperties()
        msg_props.delivery_mode = 2 # persistent message
        msg_props.content_type = "text/plain"
        return msg_props


    def send_message(self, exchange, message):
        """
            Does not work for some reason
        """
        self.channel.basic_publish(body=message,
                                   exchange=exchange,
                                   properties=self.get_message_props(),
                                   routing_key='')
        print "Message sent!"

        #close connection
        self.connection.close()

    def send_message_to_queue(self, queue, message):
        self.channel.basic_publish(body=message,
                                   exchange='',
                                   properties=self.get_message_props(),
                                   routing_key=queue)

    def bind_exchange_to_queue(self, exchange, queue):
        self.channel.queue_bind(exchange=exchange, queue=queue)

    def receive_messages_with_ack(self, callback, queue_name):
        self.channel.basic_consume(callback,
                                   queue=queue_name,
                                   no_ack=False)
        self.channel.start_consuming()
