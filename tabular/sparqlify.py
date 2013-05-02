import os

import subprocess
import threading
import Queue
import time

from config import config
from database import DatabasePlainFiles
from tabular.mapping import Mapping
from tabular.tabularfile import TabularFile


class Sparqlify():
    def __init__(self, resource_id):
        self.resource_id = resource_id
    
    def transform_resource_to_rdf(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
                
        tabular_file = TabularFile(resource_id)
        if(tabular_file.get_csv_file_path()):
            file_path = tabular_file.get_csv_file_path()
        else:
            file_path = tabular_file.download()

        mapping = Mapping(resource_id)
        mapping.init()
        mapping_path = mapping.get_mapping_path(mapping_name)
        mapping_current = mapping.get_mapping_by_name(mapping_name)
        
        if('delimiter' in mapping_current):
            delimiter = mapping_current['delimiter']
        else:
            delimiter = ','
        
        sparqlify_call = ["java",
                          "-cp", config.sparqlify_jar_path,
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
        
        #print sparqlify_call
        print str(' '.join(sparqlify_call))
        
        rdf_file = os.path.join(config.rdf_files_path, str(self.resource_id) + '_' + str(mapping_name) + '.rdf')
        f = open(rdf_file, 'w')
        process = subprocess.Popen(sparqlify_call, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #sparqlify_message = process.stderr.read()
        sparqlify_message = ""

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
                    print "Processed %d lines" % stdout_size

            # Show what we received from standard error.
            while not stderr_queue.empty():
                line = stderr_queue.get()
                print 'Received line on standard error: ' + repr(line)

            # Sleep a bit before asking the readers again.
            time.sleep(.1)

        # Let's be tidy and join the threads we've started.
        stdout_reader.join()
        stderr_reader.join()

        # Close subprocess' file descriptors.
        process.stdout.close()
        process.stderr.close()
        f.close()
        
        return sparqlify_message, process.returncode
    
    def get_rdf_file_path(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
        
        filename = resource_id + '_' + mapping_name + '.rdf'
        db = DatabasePlainFiles(config.rdf_files_path)
        if(db.is_exists(filename)):
            return db.get_path_to_file(filename)
        else:
            return False
        
    def get_rdf_file_url(self, configuration_name, resource_id=None):
        if(not resource_id):
            resource_id = self.resource_id
        file_path = self.get_rdf_file_path(configuration_name, resource_id=resource_id)
        if(file_path):
            return os.path.join(config.server_base_url, self.get_rdf_file_path(configuration_name))
        else:
            return False
        

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

if __name__ == '__main__':
    sparqlify = Sparqlify('1aa9c015-3c65-4385-8d34-60ca0a875728')
    #print sparqlify.transform_resource_to_rdf('default-tranformation-configuration')
    print sparqlify.get_rdf_file_path('default-tranformation-configuration')
    print sparqlify.get_rdf_file_url('default-tranformation-configuration')
