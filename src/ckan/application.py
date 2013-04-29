import os

from ckanclient import CkanClient

from config import config
from database import DatabasePlainFiles

#relative imports
from package import Package
from resource import Resource

class CkanApplication():
    """ Reflects the CKAN application itself,
        interfaces for getting packages etc.
    """
    def __init__(self):
        self.ckan = CkanClient(base_location=config.ckan_api_url,
                               api_key=config.ckan_api_key)
        
    def get_csv_resource_list(self):
        db = DatabasePlainFiles()
        return db.loadDbase(config.data_csv_list)

    def get_package_list(self):
        return self.ckan.package_list()

    def dump_all_resources(self):
        package_list = self.get_package_list()
        for package_name in package_list:
            pkg = Package(package_name)
            print pkg
            break

    def update_csv_resource_list(self):
        output = []
        package_list = self.get_package_list()
        
        for package_id in package_list:
            package = Package(package_id)
            for resource in package.resources:
                r = Resource(resource['id'])
                r.format = resource['format']
                if(r.is_csv()):
                    output.append(r.id)
        
        db = DatabasePlainFiles()
        db.saveDbase(config.data_csv_list, output)
        
    def get_sparqlified_list(self):
        return os.listdir(config.rdf_files_exposed_path)
        
    def update_sparqlified_list(self):
        #update list - make soft links to the files
        rdf_files = os.listdir(config.rdf_files_path)
        for rdf_file in rdf_files:
            #make a soft link
            link_to = os.path.abspath(config.rdf_files_path + rdf_file)
            resource_id = rdf_file[:36] #take resource_id part only
            link = self.rdf_files_exposed_path + resource_id
            make_soft_link = ["ln",
                              "-f",
                              "-s",
                              link_to,
                              link]
            pipe = subprocess.Popen(make_soft_link, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            print pipe_message
            
if __name__ == '__main__':
    ckan_app = CkanApplication()
    #print ckan_app.dump_all_resources()
    #print ckan_app.get_package_list()
    #print ckan_app.get_csv_resource_list()
    #print ckan_app.update_csv_resource_list()
    #print ckan_app.get_sparqlified_list()
    
