import os
import glob
import subprocess
import json

from ckanclient import CkanClient

from config import config
from config import rdf_formats
from database import DatabasePlainFiles

#relative imports
from package import Package
from resource import Resource
from tabular.mapping import Mapping
from tabular.tabularfile import TabularFile

class CkanApplication():
    """ Reflects the CKAN application itself,
        interfaces for getting packages etc.
    """
    def __init__(self):
        self.ckan = CkanClient(base_location=config.ckan_api_url,
                               api_key=config.ckan_api_key)
        
    def get_csv_resource_list_actual(self):
        csv_list = os.listdir(config.data_csv_resources_path)
        return csv_list

    def get_csv_resource_list_current(self):
        csv_list = os.listdir(config.resources_path)
        return csv_list

    def get_package_list(self):
        return self.ckan.package_list()

    def get_all_csv2rdf_page_ids(self):
        db = DatabasePlainFiles(config.data_path)
        pages = db.loadDbase('data_all_csv2rdf_pages_file')
        titles = []
        for page in pages['query']['allpages']:
            titles.append( page['title'][8:].lower() )
        return titles

    def delete_outdated_items(self):
        """
            Delete outdated wikipages and csv files
        """
        (resources_outdated, resources_new) = self.csv_resources_list_diff()
        (pages_outdated, pages_new) = self.wiki_pages_diff()
        outdated_list = pages_outdated + resources_outdated
        print len(outdated_list)
        for resource_id in outdated_list:
            mapping = Mapping(resource_id)
            try:
                print mapping.delete_wiki_page()
                print os.remove( os.path.join(config.resources_path, resource_id) )
            except BaseException as e:
                print str(e)
    
    def clean_sparqlified(self):
        resources_list = self.get_csv_resource_list_current()
        sparqlified_list = os.listdir(config.rdf_files_path)
        resources_ids_sparqlified = []
        for item in sparqlified_list:
            resources_ids_sparqlified.append(item.split("_")[0])

        outdated_sparqlified = []
        for item in resources_ids_sparqlified:
            if(not item in resources_list):
                outdated_sparqlified.append(item)
        
        for resource_id in outdated_sparqlified:
            for filename in glob.glob( os.path.join(config.rdf_files_path, resource_id+"*")):
                os.remove(filename)

    def download_new_resources(self):
        (outdated_list, new_list) = self.csv_resources_list_diff()
        for resource_id in new_list:
            print resource_id
            tabularfile = TabularFile(resource_id)
            if(tabularfile.download()): #if 200 response code
                tabularfile.validate()

    def create_new_wiki_pages(self):
        (pages_outdated, pages_new) = self.wiki_pages_diff()

        for num, page_id in enumerate(pages_new):
            mapping = Mapping(page_id)
            default_page = mapping.generate_default_wiki_page()
            mapping.create_wiki_page(default_page)

    def csv_resources_list_diff(self):
        actual_list = self.get_csv_resource_list_actual()
        current_list = self.get_csv_resource_list_current()
        resources_outdated = []
        resources_new = []

        for resource in current_list:
            if(not resource in actual_list):
                resources_outdated.append(resource)

        for resource in actual_list:
            if(not resource in current_list and
               not resource in resources_outdated):
                resources_new.append(resource)

        return (resources_outdated, resources_new)

    def wiki_pages_diff(self):
        resources_list = self.get_csv_resource_list_current()
        page_ids_list = self.get_all_csv2rdf_page_ids()
        pages_outdated = []
        pages_new = [] 

        for page_id in page_ids_list:
            if(not page_id in resources_list):
                pages_outdated.append(page_id) 

        for resource_id in resources_list:
            if(not resource_id in page_ids_list):
                pages_new.append(resource_id)

        return (pages_outdated, pages_new)

    def update_csv_resource_list(self):
        package_list = self.get_package_list()
        db = DatabasePlainFiles(config.data_csv_resources_path)

        for package_id in package_list:
            package = Package(package_id)
            for resource in package.resources:
                r = Resource(resource['id'])
                r.format = resource['format']
                if(r.is_csv()):
                    db.saveDbase(resource['id'], resource)

    def get_full_resource_list(self):
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(config.data_all_resources)

    def get_all_available_formats(self):
        resource_list = self.get_full_resource_list()
        formats = []
        for resource in resource_list:
            if(not resource['format'] in formats):
                formats.append(resource['format'])
        return sorted(formats)

    def get_rdf_resources(self):
        return self.get_resources("rdf")

    def get_rdf_compressed_resources(self):
        return self.get_resources("rdf_compressed")

    def get_rdf_html_resources(self):
        return self.get_resources("rdf_html")

    def get_rdf_endpoints_resources(self):
        return self.get_resources("endpoints")

    def get_resources(self, type):
        types = ["rdf","rdf_compressed","endpoints","rdf_html"]
        if(not type in types):
            return False
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(eval("config.data_"+str(type)))

    def get_rdf_and_sparql_list(self):
        rdf = self.get_rdf_resources()
        rdf_compressed = self.get_rdf_compressed_resources()
        rdf_html = self.get_rdf_html_resources()
        endpoints = self.get_rdf_endpoints_resources()
        process_list = rdf + rdf_compressed + rdf_html

        #Jens request: download link to rdf file, sparql end-point (if exist)
        #rdf_id, package_id, sparql_id, rdf_link, sparql_link
        #output_item = {'rdf_id': '',       # id
                       #'package_name': '', # package_name
                       #'rdf_url': '',     # url
                       #'sparql_id': '',    # (optional) also id, but in the endpoints list
                       #'sparql_url': '' } # (optional) also url, but in the endpoints list
        # order of the fields in csv output file
        fieldnames = ('rdf_id', 'sparql_id', 'package_name', 'rdf_url', 'sparql_url')
        output = []

        for resource in process_list:
            output_item = {}
            output_item['rdf_id'] = resource.id
            output_item['package_name'] = resource.package_name
            output_item['rdf_url'] = (resource.url).encode('utf-8')
            for endpoint in endpoints:
                if(resource.package_name == endpoint.package_name):
                    output_item['sparql_id'] = endpoint.id
                    output_item['sparql_url'] = endpoint.url
            output.append(output_item)
       
        db = DatabasePlainFiles(config.data_path)
        db.saveListToCSV(config.data_rdf_and_sparql_csv, output, fieldnames) 

    def update_all_rdf_resources(self):
        resource_list = self.get_full_resource_list()
        rdf = []
        rdf_compressed = []
        endpoints = []
        rdf_html = []
        for resource in resource_list:
            if(resource['format'] in rdf_formats.rdf_formats):
                res = Resource(resource['id'])
                res.init()
                rdf.append(res)
            if(resource['format'] in rdf_formats.compressed_formats):
                res = Resource(resource['id'])
                res.init()
                rdf_compressed.append(res)
            if(resource['format'] in rdf_formats.endpoints):
                res = Resource(resource['id'])
                res.init()
                endpoints.append(res)
            if(resource['format'] in rdf_formats.html_formats):
                res = Resource(resource['id'])
                res.init()
                rdf_html.append(res)
        db = DatabasePlainFiles(config.data_path)
        db.saveDbase(config.data_rdf, rdf)
        db.saveDbase(config.data_rdf_compressed, rdf_compressed)
        db.saveDbase(config.data_endpoints, endpoints)
        db.saveDbase(config.data_rdf_html, rdf_html)
        
    def update_full_resource_list(self):
        package_list = self.get_package_list()
        db = DatabasePlainFiles(config.data_path)
        all_resources = []
        number_of_datasets = len(package_list)
        print "Number of datasets in the "+str(config.ckan_base_url)+" : "+str(number_of_datasets)
        for num, package_id in enumerate(package_list):
            try:
                print "Processing package " + str(num) + " out of " + str(number_of_datasets)
                package = Package(package_id)
                for resource in package.resources:
                   all_resources.append(resource) 
                del package
            except BaseException as e:
                print str(e)
        db.saveDbase(config.data_all_resources, all_resources)

    def get_sparqlified_list(self):
        return os.listdir(config.rdf_files_exposed_path)

    def update_exposed_rdf_list(self):
        db = DatabasePlainFiles(config.root_path)
        db.saveDbaseRaw('get_exposed_rdf_list', json.dumps(self.get_sparqlified_list()))
        
    def update_sparqlified_list(self):
        #delete all items
        for file in glob.glob(os.path.join(config.rdf_files_exposed_path + "*")):
            os.remove(file)
        #update list - make soft links to the files
        rdf_files = os.listdir(config.rdf_files_path)
        for rdf_file in rdf_files:
            #make a soft link
            link_to = os.path.abspath(config.rdf_files_path + rdf_file)
            resource_id = rdf_file[:36] #take resource_id part only
            link = config.rdf_files_exposed_path + resource_id
            make_soft_link = ["ln",
                              "-f",
                              "-s",
                              link_to,
                              link]
            pipe = subprocess.Popen(make_soft_link, stdout=subprocess.PIPE)
            #pipe_message = pipe.stdout.read()

    def update_metadata_for_all_resources(self):
        resources_list = self.get_csv_resource_list_current()
        for resource_id in resources_list[2:]:
            try:
                mapping = Mapping(resource_id)
                mapping.init()
                mapping.update_metadata()
            except BaseException as e:
                print str(e)
            
if __name__ == '__main__':
    ckan_app = CkanApplication()
    ckan_app.get_rdf_and_sparql_list()
    #ckan_app.update_all_rdf_resources()
    #ckan_app.update_full_resource_list()
    #ckan_app.update_metadata_for_all_resources()
    #ckan_app.update_exposed_rdf_list()
    #ckan_app.update_sparqlified_list()
    #ckan_app.clean_sparqlified()
    #ckan_app.create_new_wiki_pages()
    #ckan_app.wiki_pages_diff()
    #ckan_app.get_csv2rdf_pages()
    #ckan_app.download_new_resources()
    #ckan_app.delete_outdated_items()
    #ckan_app.delete_outdated_wiki_pages()
    #print ckan_app.csv_resources_list_diff()
    #print ckan_app.dump_all_resources()
    #print ckan_app.get_package_list()
    #print len(ckan_app.get_csv_resource_list())
    #print ckan_app.update_csv_resource_list()
    #print ckan_app.get_sparqlified_list()
    
