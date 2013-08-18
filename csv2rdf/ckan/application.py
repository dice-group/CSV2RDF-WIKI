import os
import glob
import subprocess
import logging

from ckanclient import CkanClient

import csv2rdf.config

import csv2rdf.tabular.mapping
import csv2rdf.tabular.tabularfile
import csv2rdf.ckan.ckanio
import csv2rdf.ckan.ckanio.queries

class CkanApplication():
    """ 
        Contains service functions (batch deleting, creating etc.)
    """
    def __init__(self):
        self.ckan = CkanClient(base_location=csv2rdf.config.config.ckan_api_url,
                               api_key=csv2rdf.config.config.ckan_api_key)

    def update(self):
        """
            Dump the CKAN instance in the files
            see log in the config.log
        """
        logging.info("Dumping data from the CKAN ... Started.")
        io = csv2rdf.ckan.ckanio.CkanIO()
        io.update_full_package_list()
        io.update_full_resource_list()
        io.update_csv_resource_list()
        io.update_rdf_resources_list()
        logging.info("Dumping data from the CKAN ... Complete.")

        logging.info("Updating the list of wiki pages ... Started.")
        mapping = csv2rdf.tabular.mapping.Mapping('')
        mapping.update_csv2rdf_wiki_page_list()
        logging.info("Updating the list of wiki pages ... Complete.")

    def synchronize(self):
        """
            Delete outdated resources and wiki pages
            Download new resources, clean them up and
            Create wiki pages for them
            Refresh sparqlified list
        """
        q = csv2rdf.ckan.ckanio.queries.Queries()
        (outdated_csv, new_csv) = q.get_outdated_and_new_csv_resources()

        mapping = csv2rdf.tabular.mapping.Mapping('')
        (outdated_wiki_pages, new_wiki_pages) = mapping.get_outdated_and_new_wiki_pages()

        #Delete outdated resources
        self.delete_outdated_items(outdated_csv, outdated_wiki_pages)
        self.remove_outdated_rdf()

        self.download_and_validate_new_resources(new_csv)
        (outdated_wiki_pages, new_wiki_pages) = mapping.get_outdated_and_new_wiki_pages()
        self.create_new_wiki_pages(new_wiki_pages)
        self.update_sparqlified_list()

    def delete_outdated_items(self, outdated_csv, outdated_wiki_pages):
        """
            Delete outdated wikipages and csv files
        """
        logging.info("Deleting outdated resources ... Started.")
        outdated_list = outdated_csv + outdated_wiki_pages
        logging.info("Number of outdated resources and pages to delete: %d" % len(outdated_list))
        for resource_id in outdated_list:
            logging.info("Processing resource %s" % resource_id)
            mapping = csv2rdf.tabular.mapping.Mapping(resource_id)
            try:
                delete_result = mapping.delete_wiki_page()
                logging.info("Removing the wiki page ... %s" % delete_result)
                os.remove( os.path.join(csv2rdf.config.config.resources_path, resource_id) )
                logging.info("File removed successfully.")
            except BaseException as e:
                logging.info("An exception occurred, while deleting item: %s" % str(e))
        logging.info("Deleting outdated resources ... Complete.")
    
    def remove_outdated_rdf(self):
        logging.info("Removing outdated RDF files ... Started.")
        tf = csv2rdf.tabular.tabularfile.TabularFile('')
        resources_list = tf.get_csv_resource_list_local()
        sparqlified_list = os.listdir(csv2rdf.config.config.rdf_files_path)
        resources_ids_sparqlified = []
        for item in sparqlified_list:
            resources_ids_sparqlified.append(item.split("_")[0])

        outdated_sparqlified = []
        for item in resources_ids_sparqlified:
            if(not item in resources_list):
                outdated_sparqlified.append(item)

        logging.info("Outdated RDF files found: %d" % len(outdated_sparqlified))
        
        for resource_id in outdated_sparqlified:
            for filename in glob.glob( os.path.join(csv2rdf.config.config.rdf_files_path, resource_id+"*")):
                logging.info("Removing %s" % filename)
                os.remove(filename)

        logging.info("Removing outdated RDF files ... Complete.")

    def download_and_validate_new_resources(self, new_resources):
        logging.info("Downloading new resources ... Started.")
        logging.info("Resources to process %d" % len(new_resources))
        for num, resource_id in enumerate(new_resources):
            logging.info("Processing resource: %s" % resource_id)
            logging.info("%d left to process." % (len(new_resources) - num + 1))
            tabularfile = csv2rdf.tabular.tabularfile.TabularFile(resource_id)
            if(tabularfile.download()): #if 200 response code
                tabularfile.validate()
        logging.info("Downloading new resources ... Complete.")

    def create_new_wiki_pages(self, new_wiki_page_ids):
        logging.info("Creating new wiki mappings for CSV resources ... Started.")
        for num, page_id in enumerate(new_wiki_page_ids):
            logging.info("Creating page for %s" % page_id)
            mapping = csv2rdf.tabular.mapping.Mapping(page_id)
            default_page = mapping.generate_default_wiki_page()
            mapping.create_wiki_page(default_page)
            break
        logging.info("Creating new wiki mappings for CSV resources ... Complete.")

    def update_sparqlified_list(self):
        #delete all items
        for file in glob.glob(os.path.join(csv2rdf.config.config.rdf_files_exposed_path + "*")):
            os.remove(file)
        #update list - make soft links to the files
        rdf_files = os.listdir(csv2rdf.config.config.rdf_files_path)
        for rdf_file in rdf_files:
            #make a soft link
            link_to = os.path.abspath(csv2rdf.config.config.rdf_files_path + rdf_file)
            resource_id = rdf_file[:36] #take resource_id part only
            link = csv2rdf.config.config.rdf_files_exposed_path + resource_id
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
                mapping = csv2rdf.tabular.mapping.Mapping(resource_id)
                mapping.init()
                mapping.update_metadata()
            except BaseException as e:
                print str(e)
            
if __name__ == '__main__':
    ckan_app = CkanApplication()

    #ckan_app.create_new_wiki_pages()
    ckan_app.synchronize()
    #ckan_app.update()
    #ckan_app.clean_sparqlified()

    #print ckan_app.get_rdf_for_lodstats()
    #ckan_app.get_resource_data()
    #ckan_app.get_rdf_and_sparql_list()
    #ckan_app.update_all_rdf_resources()
    #ckan_app.update_full_resource_list()
    #ckan_app.update_metadata_for_all_resources()
    #ckan_app.update_exposed_rdf_list()
    #ckan_app.update_sparqlified_list()
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
    
