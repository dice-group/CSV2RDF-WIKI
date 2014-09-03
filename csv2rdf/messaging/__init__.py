import pika

class Messaging(object):
    def __init__(self):
        self.connection = self.connectToRabbit()
        self.channel = self.retrieveChannel(self.connection)

    def connectToRabbit(self):
        credentials = pika.PlainCredentials("guest","guest")
        connectionParams = pika.ConnectionParameters("localhost", credentials=credentials)
        connection = pika.BlockingConnection(connectionParams)
        return connection

    def retrieveChannel(self, connection):
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1) # do not send next msg before ack
        return channel

    def declareDirectExchange(self, name):
        self.channel.exchange_declare(exchange=name,
                                      type="direct",
                                      passive=False, #will create exchange if does not exist
                                      durable=True,
                                      auto_delete=False)

    def declareQueue(self, name):
        self.channel.queue_declare(queue=name)

    def getMessageProps(self):
        messageProperties = pika.BasicProperties()
        messageProperties.delivery_mode = 2 # persistent message
        messageProperties.content_type = "text/plain"
        return messageProperties


    def sendMessage(self, exchange, message):
        """
            Does not work for some reason
        """
        self.channel.basic_publish(body=message,
                                   exchange=exchange,
                                   properties=self.getMessageProps(),
                                   routing_key='')
        print "Message sent!"

        #close connection
        self.connection.close()

    def sendMessageToQueue(self, queue, message):
        self.channel.basic_publish(body=message,
                                   exchange='',
                                   properties=self.getMessageProps(),
                                   routing_key=queue)

    def bindExchangeToQueue(self, exchange, queue):
        self.channel.queue_bind(exchange=exchange, queue=queue)

    def receiveMessagesWithAck(self, callback, queue_name):
        self.channel.basic_consume(callback,
                                   queue=queue_name,
                                   no_ack=False)
        self.channel.start_consuming()
