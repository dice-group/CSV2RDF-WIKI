import logging

from ckanclient import CkanClient

import csv2rdf.database
import csv2rdf.ckan.resource
import csv2rdf.ckan.package

import csv2rdf.config
import csv2rdf.config.config
import csv2rdf.config.rdf_formats

class CkanIO():
    def __init__(self):
        self.ckan = CkanClient(base_location=csv2rdf.config.config.ckan_api_url,
                               api_key=csv2rdf.config.config.ckan_api_key)

    def get_package_list(self):
        """
            Returns the list of package names (unique identifiers)
        """
        return self.ckan.package_list()

    def update_full_package_list(self):
        full_package_list = []
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_packages_path)
        package_list = self.get_package_list()
        for num, package_id in enumerate(package_list):
            try:
                package = db.loadDbase(package_id)
                full_package_list.append(package)
            except BaseException as e:
                logging.error("An exception occured, while loading package, try CkanIO.update_packages")
                logging.error(str(e))
        db.saveDbase(csv2rdf.config.config.data_full_package_list, full_package_list)
            
    def update_packages(self):
        """
            Dump the CKAN instance into the files
        """
        package_list = self.get_package_list()
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_packages_path)
        number_of_packages = len(package_list)
        for num, package_id in enumerate(package_list):
            logging.info("processing %d out of %d package" % (num + 1, number_of_packages))
            try:
                package = csv2rdf.ckan.package.Package(package_id)
                # ckan object can not be pickled
                del package.ckan 
                db.saveDbase(package_id, package)
            except BaseException as e:
                logging.info("An exception occured, while processing package %d, %s" % (num+1, package_id))
                logging.info("Exception: %s" % str(e))

        logging.info("DONE!")

    def get_full_package_list(self):
        """
            Returns the full package list (CKAN dump)
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        return db.loadDbase(csv2rdf.config.config.data_full_package_list)

    def update_full_resource_list(self):
        """
            Read the data from config.data_all_packages (CKAN full dump)
            and save resources separately in one file
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        all_packages = self.get_full_package_list()
        all_resources = []
        logging.info("Updating full resource list: %s" % csv2rdf.config.config.data_full_resource_list)
        for num, package in enumerate(all_packages):
            for resource in package.resources:
               all_resources.append(resource) 
        db.saveDbase(csv2rdf.config.config.data_full_resource_list, all_resources)
        logging.info("DONE!")

    def get_full_resource_list(self):
        """
            Returns the list of all resources (CKAN dump)
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        return db.loadDbase(csv2rdf.config.config.data_full_resource_list)

    def update_csv_resource_list(self):
        """
            Read the data from config.data_all_resources and 
            Save the list of all CSV resources
        """
        all_resources = self.get_full_resource_list()
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        csv_resources = []

        logging.info("Updating CSV resource list: %s" % csv2rdf.config.config.data_csv_resource_list)
        for resource in all_resources:
            r = csv2rdf.ckan.resource.Resource(resource['id'])
            r.init_from_dump(resource)
            if(r.is_csv()):
                csv_resources.append(resource)

        db.saveDbase(csv2rdf.config.config.data_csv_resource_list, csv_resources)
        logging.info("DONE!")

    def get_csv_resource_list(self):
        """
            Returns the list of available csv CKAN resources (dumps)
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        return db.loadDbase(csv2rdf.config.config.data_csv_resources)

    def update_rdf_resources_list(self):
        """
            Update the list of the RDF resources
        """
        resource_list = self.get_full_resource_list()
        rdf = []
        rdf_compressed = []
        endpoints = []
        rdf_html = []
        logging.info("Updating RDF resource list: %s" % csv2rdf.config.config.data_rdf_resource_list)
        logging.info("Updating RDF resource list: %s" % csv2rdf.config.config.data_rdf_compressed_resource_list)
        logging.info("Updating RDF resource list: %s" % csv2rdf.config.config.data_endpoint_resource_list)
        logging.info("Updating RDF resource list: %s" % csv2rdf.config.config.data_rdf_html_resource_list)
        for resource in resource_list:
            if(resource['format'] in csv2rdf.config.rdf_formats.rdf_formats):
                res = csv2rdf.ckan.resource.Resource(resource['id'])
                res.init_from_dump(resource)
                rdf.append(res)
            if(resource['format'] in csv2rdf.config.rdf_formats.compressed_formats):
                res = csv2rdf.ckan.resource.Resource(resource['id'])
                res.init_from_dump(resource)
                rdf_compressed.append(res)
            if(resource['format'] in csv2rdf.config.rdf_formats.endpoints):
                res = csv2rdf.ckan.resource.Resource(resource['id'])
                res.init_from_dump(resource)
                endpoints.append(res)
            if(resource['format'] in csv2rdf.config.rdf_formats.html_formats):
                res = csv2rdf.ckan.resource.Resource(resource['id'])
                res.init_from_dump(resource)
                rdf_html.append(res)
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        db.saveDbase(csv2rdf.config.config.data_rdf_resource_list, rdf)
        db.saveDbase(csv2rdf.config.config.data_rdf_compressed_resource_list, rdf_compressed)
        db.saveDbase(csv2rdf.config.config.data_endpoint_resource_list, endpoints)
        db.saveDbase(csv2rdf.config.config.data_rdf_html_resource_list, rdf_html)
        logging.info("DONE!")

    def get_resource_list(self, type):
        types = ["rdf","rdf_compressed","endpoint","rdf_html"]
        if(not type in types):
            return False
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_path)
        return db.loadDbase(eval("csv2rdf.config.config.data_"+str(type)+"_resources"))

if __name__ == "__main__":
    import sys

    #root = logging.getLogger()

    #ch = logging.StreamHandler(sys.stdout)
    #ch.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #ch.setFormatter(formatter)
    #root.addHandler(ch)

    io = CkanIO()

    #io.get_package_list()
    io.update_packages()
    #io.update_full_package_list()
    #print io.get_full_package_list()
    #io.update_full_resource_list()
    #io.get_full_resource_list()
    #io.update_csv_resource_list()
    #io.get_csv_resource_list()
    #io.update_rdf_resources_list()
    #io.get_resource_list("rdf")
