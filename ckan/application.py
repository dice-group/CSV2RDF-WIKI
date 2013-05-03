import os
import glob
import subprocess
import json

from ckanclient import CkanClient

from config import config
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
            
if __name__ == '__main__':
    ckan_app = CkanApplication()
    ckan_app.update_exposed_rdf_list()
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
    
