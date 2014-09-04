import os

import json
import logging
import subprocess
import Queue
import time

import csv2rdf.config
import csv2rdf.database
import csv2rdf.tabular.mapping
import csv2rdf.tabular.tabularfile
import csv2rdf.messaging
import csv2rdf.csv.validation
from csv2rdf.virtuoso.load import VirtuosoLoader
from csv2rdf.tabular.async import AsynchronousFileReader

class Sparqlify(object):
    def __init__(self, resourceId):
        self.resourceId = resourceId
    
    def addResourceToProcessingQueue(self, mappingName, resourceId = None):
        """
            Send the message to the queue
        """
        if(not resourceId):
            resourceId = self.resourceId

        #send message to one of the java handlers
        exchange = "sparqlify_java_exchange"
        queue = "sparqlify_java_queue"
        messageBroker = csv2rdf.messaging.Messaging()
        messageBroker.declareDirectExchange(exchange)
        messageBroker.declareQueue(queue)
        messageBroker.bindExchangeToQueue(exchange, queue)
        message = json.dumps({'mappingName': mappingName, 'resourceId': resourceId})
        #message_broker.send_message(exchange, message)
        messageBroker.sendMessageToQueue(queue, message)
        return True #Message sent!
    
    def getRdfFilePath(self, mappingName, resourceId = None):
        if(not resourceId):
            resourceId = self.resourceId
        
        filename = resourceId + '_' + mappingName + '.rdf'
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.rdf_files_path)
        if(db.is_exists(filename)):
            return db.get_path_to_file(filename)
        else:
            return False
        
    def getRdfFileUrl(self, mappingName, resourceId=None):
        if(not resourceId):
            resourceId = self.resourceId

        rdfFilePath = self.getRdfFilePath(mappingName, resourceId=resourceId)
        if(filePath):
            return os.path.join(csv2rdf.config.config.server_base_url, rdfFilePath)
        else:
            return False

    def getSparqlifiedList(self):
        return os.listdir(csv2rdf.config.config.rdf_files_exposed_path)

    def updateExposedRdfList(self):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.root_path)
        db.saveDbaseRaw('get_exposed_rdf_list', json.dumps(self.getSparqlifiedList()))

    def validateCsv(self, resourceId, mappingName):
        validator = csv2rdf.csv.validation.CsvDatatypeValidator(resourceId, mappingName)
        return validator.validate()

    def transformResourceToRdf(self, mappingName, resourceId = None):
        if(not resourceId):
            resourceId = self.resourceId
                
        logging.info("Getting the CSV filepath...")
        tabularFile = csv2rdf.tabular.tabularfile.TabularFile(resourceId)
        filePath = tabularFile.getCsvFilePathDownload()

        logging.info("Fetching the mapping...")
        mapping = csv2rdf.tabular.mapping.Mapping(resourceId)
        mapping.init()
        mappingPath = mapping.get_mapping_path(mappingName)
        mappingCurrent = mapping.get_mapping_by_name(mappingName)

        #validate cSV to comply with xsd types
        logging.info("Validating CSV...")
        filePath = self.validateCsv(resourceId, mappingName)
        logging.info("Validated CSV is: %s" % (filePath,))

        #process file based on the mapping_current options
        processedFile = mapping.process_file(filePath, mappingCurrent)
        filePath = str(processedFile.name)
        delimiter = mappingCurrent['delimiter']
        
        sparqlifyCall = ["java",
                         "-cp", csv2rdf.config.config.sparqlify_jar_path,
                         "org.aksw.sparqlify.csv.CsvMapperCliMain",
                         "-f", filePath,
                         "-c", mappingPath,
                         "-s", delimiter,
                         "-h"]
        # -h - header omit
        # -d - delimiter ("")
        # -s - separator (@,;)
        # for your strange file with all the @, you could try: -s @ -d \0 -e \1 (\0 \1 - binary 0 and 1)
        # \123 or hex e.g. 0xface if you need
        
        logging.info(str(' '.join(sparqlifyCall)))

        rdfFile = os.path.join(csv2rdf.config.config.rdf_files_path, str(resourceId) + '_' + str(mappingName) + '.rdf')
        f = open(rdfFile, 'w')
        process = subprocess.Popen(sparqlifyCall, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("rdfFile: %s" % rdfFile)

        stdoutQueue = Queue.Queue()
        stdoutReader = AsynchronousFileReader(process.stdout, stdoutQueue)
        stdoutReader.start()
        stderrQueue = Queue.Queue()
        stderrReader = AsynchronousFileReader(process.stderr, stderrQueue)
        stderrReader.start()

        stdoutSize = 0

        while not stdoutReader.eof() or not stderrReader.eof():
            # Show what we received from standard output.
            while not stdoutQueue.empty():
                stdoutSize += 1
                line = stdoutQueue.get()
                f.write(line)
                if(stdoutSize % 1000 == 0):
                    logging.info("Processed %d lines of %s" % (stdoutSize, rdfFile))
                    

            # Show what we received from standard error.
            while not stderrQueue.empty():
                line = stderrQueue.get()
                logging.info('Received line on standard error: ' + repr(line))

            # Sleep a bit before asking the readers again.
            time.sleep(.1)

        # Let's be tidy and join the threads we've started.
        stdoutReader.join()
        stderrReader.join()

        # Close subprocess' file descriptors.
        process.stdout.close()
        process.stderr.close()
        f.close()
        
        #update metadata_
        logging.info("updating metadata...")
        mapping.updateMetadata(resourceId, mappingName)
        logging.info("DONE")

        #upload to triplestore
        logging.warn("loading resource to virtuoso!")
        virtuoso = VirtuosoLoader()
        graphUri = "http://data.publicdata.eu/%s/%s" % (str(resourceId),str(mappingName))
        virtuoso.reload(rdfFile, graphUri)
        
        return process.returncode

if __name__ == '__main__':
    #send message to queue for testing
    #testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    #sparqlify = Sparqlify(testResourceId)
    #testMapping = "csv2rdf-interface-generated"
    #print sparqlify.addResourceToProcessingQueue(testMapping)

    #transformation test
    testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    sparqlify = Sparqlify(testResourceId)
    testMapping = "csv2rdf-interface-generated"
    print sparqlify.transformResourceToRdf(testMapping)
