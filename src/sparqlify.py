from tabularfile import TabularFile
from mapping import Mapping
import config
import os
import subprocess
from database import Database

class Sparqlify():
    def __init__(self, resource_id):
        self.resource_id = resource_id
    
    def transform_resource_to_rdf(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
        
        tabular_file = TabularFile(resource_id)
        file_path = tabular_file.get_csv_file_path()
        
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
                          "-d", delimiter]
        
        print str(' '.join(sparqlify_call))
        
        rdf_file = os.path.join(config.rdf_files_path, str(self.resource_id) + '_' + str(mapping_name) + '.rdf')
        f = open(rdf_file, 'w')
        pipe = subprocess.Popen(sparqlify_call, shell=False, stdout=f, stderr=subprocess.PIPE)
        sparqlify_message = pipe.stderr.read()
        pipe.stderr.close()
        f.close()
        
        return sparqlify_message, pipe.returncode
    
    def get_rdf_file_path(self, mapping_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
        
        filename = resource_id + '_' + mapping_name + '.rdf'
        db = Database(config.rdf_files_path)
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
        
if __name__ == '__main__':
    sparqlify = Sparqlify('1aa9c015-3c65-4385-8d34-60ca0a875728')
    #print sparqlify.transform_resource_to_rdf('default-tranformation-configuration')
    print sparqlify.get_rdf_file_path('default-tranformation-configuration')
    print sparqlify.get_rdf_file_url('default-tranformation-configuration')