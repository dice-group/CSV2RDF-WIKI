import logging
import json

import csv2rdf.tabular.sparqlify

class SparqlifyJavaHandler(object):
    def __init__(self, resourceId, mappingName):
        self.resourceId = resourceId
        self.mappingName = mappingName

    def processResource(self):
        logging.info("Processing %s %s" % (self.mappingName, self.resourceId))
        print "Processing %s %s" % (self.mappingName, self.resourceId)
        #try:
        print "init sparqlify"
        sparqlify = csv2rdf.tabular.sparqlify.Sparqlify(self.resourceId)
        print "start processing"
        processReturnCode = sparqlify.transformResourceToRdf(self.mappingName, self.resourceId)
        logging.info("Process returned %s" % processReturnCode)
        print "Process returned %s" % processReturnCode
        return True
        #except BaseException as e:
        #    logging.error("Exception occured while file processing: %s" % str(e))
        #    print "Exception occured while file processing: %s" % str(e)

    def fileIsExists(self):
        tabular_file = csv2rdf.tabular.tabularfile.TabularFile(self.resourceId)
        return tabular_file.is_exists()

def messagingCallback(ch, method, properties, body):
    logging.info("[x] Received %r" % (body,))
    print "[x] Received %r" % (body,)
    payload = json.loads(body)
    resourceId = payload["resourceId"]
    mappingName = payload["mappingName"]
    sparqlifyJavaHandler = SparqlifyJavaHandler(resourceId, mappingName)
    if(sparqlifyJavaHandler.fileIsExists()):
        logging.info("Started resource processing...")
        sparqlifyJavaHandler.processResource()
        #send ack
        ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
        logging.info("File does not exist... Deleting message from queue")
        ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__":
    exchange = "sparqlify_java_exchange"
    queue = "sparqlify_java_queue"

    messageBroker = csv2rdf.messaging.Messaging()
    messageBroker.declareDirectExchange(exchange)
    messageBroker.declareQueue(queue)
    messageBroker.bindExchangeToQueue(exchange, queue)
    print "Waiting for messages..."
    messageBroker.receiveMessagesWithAck(messagingCallback, queue)

