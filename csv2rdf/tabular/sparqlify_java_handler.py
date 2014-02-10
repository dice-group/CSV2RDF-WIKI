import threading
import Queue
import csv2rdf.tabular.tabularfile
import csv2rdf.tabular.mapping
import csv2rdf.messaging
import csv2rdf.config
import logging
import time
import subprocess
import os
import json

class SparqlifyJavaHandler(object):
    def __init__(self, resource_id, mapping_name):
        self.resource_id = resource_id
        self.mapping_name = mapping_name

    def process_resource(self):
        logging.info("Processing %s %s" % (self.mapping_name, self.resource_id))
        process_return_code = self.transform_resource_to_rdf(self.mapping_name, self.resource_id)
        print "Process returned %s" % process_return_code

    def file_is_exists(self):
        tabular_file = csv2rdf.tabular.tabularfile.TabularFile(self.resource_id)
        return tabular_file.is_exists()

    def transform_resource_to_rdf(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
                
        tabular_file = csv2rdf.tabular.tabularfile.TabularFile(resource_id)
        if(tabular_file.get_csv_file_path()):
            file_path = tabular_file.get_csv_file_path()
        else:
            file_path = tabular_file.download()

        mapping = csv2rdf.tabular.mapping.Mapping(resource_id)
        mapping.init()
        mapping_path = mapping.get_mapping_path(mapping_name)
        mapping_current = mapping.get_mapping_by_name(mapping_name)

        #process file based on the mapping_current options
        processed_file = mapping.process_file(file_path, mapping_current)
        file_path = str(processed_file.name)
        delimiter = mapping_current['delimiter']
        
        sparqlify_call = ["java",
                          "-cp", csv2rdf.config.config.sparqlify_jar_path,
                          "org.aksw.sparqlify.csv.CsvMapperCliMain",
                          "-f", file_path,
                          "-c", mapping_path,
                          "-s", delimiter,
                          "-h"]
        # -h - header omit
        # -d - delimiter ("")
        # -s - separator (@,;)
        # for your strange file with all the @, you could try: -s @ -d \0 -e \1 (\0 \1 - binary 0 and 1)
        # \123 or hex e.g. 0xface if you need
        
        logging.info(str(' '.join(sparqlify_call)))

        rdf_file = os.path.join(csv2rdf.config.config.rdf_files_path, str(self.resource_id) + '_' + str(mapping_name) + '.rdf')
        f = open(rdf_file, 'w')
        process = subprocess.Popen(sparqlify_call, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("rdf_file: %s" % rdf_file)

        stdout_queue = Queue.Queue()
        stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
        stdout_reader.start()
        stderr_queue = Queue.Queue()
        stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
        stderr_reader.start()

        stdout_size = 0

        while not stdout_reader.eof() or not stderr_reader.eof():
            # Show what we received from standard output.
            while not stdout_queue.empty():
                stdout_size += 1
                line = stdout_queue.get()
                f.write(line)
                if(stdout_size % 1000 == 0):
                    logging.info("Processed %d lines of %s" % (stdout_size, rdf_file))
                    

            # Show what we received from standard error.
            while not stderr_queue.empty():
                line = stderr_queue.get()
                logging.info('Received line on standard error: ' + repr(line))

            # Sleep a bit before asking the readers again.
            time.sleep(.1)

        # Let's be tidy and join the threads we've started.
        stdout_reader.join()
        stderr_reader.join()

        # Close subprocess' file descriptors.
        process.stdout.close()
        process.stderr.close()
        f.close()
        
        #update metadata
        mapping.update_metadata()
        
        return process.returncode

class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()
    

def messaging_callback(ch, method, properties, body):
    print "[x] Received %r" % (body,)
    payload = json.loads(body)
    resource_id = payload["resource_id"]
    mapping_name = payload["mapping_name"]
    sparqlify_java_handler = SparqlifyJavaHandler(resource_id, mapping_name)
    if(sparqlify_java_handler.file_is_exists()):
        print "Started resource processing..."
        sparqlify_java_handler.process_resource()
        #send ack
        ch.basic_ack(delivery_tag = method.delivery_tag)
    else:
        print "File does not exist... Deleting message from queue"
        ch.basic_ack(delivery_tag = method.delivery_tag)

if __name__ == "__main__":
    exchange = "sparqlify_java_exchange"
    queue = "sparqlify_java_queue"

    message_broker = csv2rdf.messaging.Messaging()
    message_broker.declare_direct_exchange(exchange)
    message_broker.declare_queue(queue)
    message_broker.bind_exchange_to_queue(exchange, queue)
    print "Waiting for messages..."
    message_broker.receive_messages_with_ack(messaging_callback, queue)

