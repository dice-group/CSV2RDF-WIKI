import os

import json
import logging

import csv2rdf.config
import csv2rdf.database
import csv2rdf.tabular.mapping
import csv2rdf.tabular.tabularfile
import csv2rdf.messaging


class Sparqlify(object):
    def __init__(self, resource_id):
        self.resource_id = resource_id
    
    def transform_resource_to_rdf(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id

        #send message to one of the java handlers
        exchange = "sparqlify_java_exchange"
        queue = "sparqlify_java_queue"
        message_broker = csv2rdf.messaging.Messaging()
        message_broker.declare_direct_exchange(exchange)
        message_broker.declare_queue(queue)
        message_broker.bind_exchange_to_queue(exchange, queue)
        message = json.dumps({'mapping_name': mapping_name, 'resource_id': resource_id})
        #message_broker.send_message(exchange, message)
        message_broker.send_message_to_queue(queue, message)

        return True #Message sent!
    
    def get_rdf_file_path(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
        
        filename = resource_id + '_' + mapping_name + '.rdf'
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.rdf_files_path)
        if(db.is_exists(filename)):
            return db.get_path_to_file(filename)
        else:
            return False
        
    def get_rdf_file_url(self, configuration_name, resource_id=None):
        if(not resource_id):
            resource_id = self.resource_id
        file_path = self.get_rdf_file_path(configuration_name, resource_id=resource_id)
        if(file_path):
            return os.path.join(csv2rdf.config.config.server_base_url, self.get_rdf_file_path(configuration_name))
        else:
            return False

    def get_sparqlified_list(self):
        return os.listdir(csv2rdf.config.config.rdf_files_exposed_path)

    def update_exposed_rdf_list(self):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.root_path)
        db.saveDbaseRaw('get_exposed_rdf_list', json.dumps(self.get_sparqlified_list()))


if __name__ == '__main__':
    testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    sparqlify = Sparqlify(testResourceId)
    testMapping = "csv2rdf-interface-generated"
    print sparqlify.transform_resource_to_rdf(testMapping)
    #print sparqlify.get_rdf_file_path('default-tranformation-configuration')
    #print sparqlify.get_rdf_file_url('default-tranformation-configuration')
