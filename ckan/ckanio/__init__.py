import logging

from ckanclient import CkanClient
from database import DatabasePlainFiles
from ckan.resource import Resource
from ckan.package import Package

from config import config
from config import rdf_formats

class CkanIO():
    def __init__(self):
        self.ckan = CkanClient(base_location=config.ckan_api_url,
                               api_key=config.ckan_api_key)

    def get_package_list(self):
        """
            Returns the list of package names (unique identifiers)
        """
        return self.ckan.package_list()

    def update_full_package_list(self):
        """
            Dump the CKAN instance into the files
        """
        package_list = self.get_package_list()
        db = DatabasePlainFiles(config.data_path)
        all_packages = []
        number_of_packages = len(package_list)
        for num, package_id in enumerate(package_list):
            logging.info("processing %d out of %d package" % (num + 1, number_of_packages))
            try:
                package = Package(package_id)
                # ckan object can not be pickled
                del package.ckan 
                all_packages.append(package)
            except BaseException as e:
                logging.info("An exception occured, while processing package %d, %s" % (num+1, package_id))
                logging.info("Exception: %s" % str(e))

        db.saveDbase(config.data_all_packages, all_packages)
        logging.info("DONE!")

    def get_full_package_list(self):
        """
            Returns the full package list (CKAN dump)
        """
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(config.data_all_packages)

    def update_full_resource_list(self):
        """
            Read the data from config.data_all_packages (CKAN full dump)
            and save resources separately in one file
        """
        db = DatabasePlainFiles(config.data_path)
        all_packages = self.get_full_package_list()
        all_resources = []
        logging.info("Updating full resource list: %s" % config.data_all_resources)
        for num, package in enumerate(all_packages):
            for resource in package.resources:
               all_resources.append(resource) 
        db.saveDbase(config.data_all_resources, all_resources)
        logging.info("DONE!")

    def get_full_resource_list(self):
        """
            Returns the list of all resources (CKAN dump)
        """
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(config.data_all_resources)

    def update_csv_resource_list(self):
        """
            Read the data from config.data_all_resources and 
            Save the list of all CSV resources
        """
        all_resources = self.get_full_resource_list()
        db = DatabasePlainFiles(config.data_path)
        csv_resources = []

        logging.info("Updating CSV resource list: %s" % config.data_csv_resources)
        for resource in all_resources:
            r = Resource(resource['id'])
            r.init_from_dump(resource)
            if(r.is_csv()):
                csv_resources.append(resource)

        db.saveDbase(config.data_csv_resources, csv_resources)
        logging.info("DONE!")

    def get_csv_resource_list(self):
        """
            Returns the list of available csv CKAN resources (dumps)
        """
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(config.data_csv_resources)

    def update_rdf_resources_list(self):
        """
            Update the list of the RDF resources
        """
        resource_list = self.get_full_resource_list()
        rdf = []
        rdf_compressed = []
        endpoints = []
        rdf_html = []
        logging.info("Updating RDF resource list: %s" % config.data_rdf_resources)
        logging.info("Updating RDF resource list: %s" % config.data_rdf_compressed_resources)
        logging.info("Updating RDF resource list: %s" % config.data_endpoint_resources)
        logging.info("Updating RDF resource list: %s" % config.data_rdf_html_resources)
        for resource in resource_list:
            if(resource['format'] in rdf_formats.rdf_formats):
                res = Resource(resource['id'])
                res.init_from_dump(resource)
                rdf.append(res)
            if(resource['format'] in rdf_formats.compressed_formats):
                res = Resource(resource['id'])
                res.init_from_dump(resource)
                rdf_compressed.append(res)
            if(resource['format'] in rdf_formats.endpoints):
                res = Resource(resource['id'])
                res.init_from_dump(resource)
                endpoints.append(res)
            if(resource['format'] in rdf_formats.html_formats):
                res = Resource(resource['id'])
                res.init_from_dump(resource)
                rdf_html.append(res)
        db = DatabasePlainFiles(config.data_path)
        db.saveDbase(config.data_rdf_resources, rdf)
        db.saveDbase(config.data_rdf_compressed_resources, rdf_compressed)
        db.saveDbase(config.data_endpoint_resources, endpoints)
        db.saveDbase(config.data_rdf_html_resources, rdf_html)
        logging.info("DONE!")

    def get_resource_list(self, type):
        types = ["rdf","rdf_compressed","endpoint","rdf_html"]
        if(not type in types):
            return False
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(eval("config.data_"+str(type)+"_resources"))

if __name__ == "__main__":
    io = CkanIO()

    #io.get_package_list()
    #io.update_full_package_list()
    #print io.get_full_package_list()
    #io.update_full_resource_list()
    #io.get_full_resource_list()
    #io.update_csv_resource_list()
    #io.get_csv_resource_list()
    #io.update_rdf_resources_list()
    #io.get_resource_list("rdf")
