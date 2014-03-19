import re

import json
import requests
import logging

import csv2rdf.config.config
import csv2rdf.interfaces

#For metadata export
import RDF
from csv2rdf.ckan.package import Package

logger = logging.getLogger(__name__)

class Resource(csv2rdf.interfaces.AuxilaryInterface):
    """ Reflects the CKAN resource.
        Properties:
            resource_group_id, cache_last_updated, revision_timestamp,
            api, webstore_last_updates, id, size, state, hash, description,
            format, tracking_summary, mimetype_inner, mimetype, cache_url,
            name, created, url, webstore_url, last_modified,
            position, revision_id, resource_type, package_name

            description - actual description of the resource
            format - can be csv, CSV, csv/text etc.
            tracking_summary: {u'total': 0, u'recent': 0}
            url - the download link
            position - position in the package if there are several resources
            package_name - necessary to initialize Package class
            ckan_base_url - http://publicdata.eu
            api_url - http://publicdata.eu/api
    """

    def __init__(self, resource_id):
        self.id = resource_id
        self.filename = self.id

    def init_from_dump(self, dump):
        self.unpack_object_to_self(dump)

    def init(self):
        #Load resource from the CKAN
        self.unpack_object_to_self(self.load_from_ckan())
        self.package_name = self.request_package_name()
        self.ckan_url = self.get_ckan_url()
        self.wiki_url = self.get_wiki_url()

    def load_from_ckan(self):
        """
            Get the resource
            specified by resource_id
            from config.ckan_api_url
        """
        data = json.dumps({'id': self.id})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = csv2rdf.config.config.ckan_api_url + '/action/resource_show'
        r = requests.post(url, timeout=csv2rdf.config.config.ckan_request_timeout, data=data, headers=headers)
        assert r.ok, r
        resource = json.loads(r.content)
        resource = resource["result"]
        return resource

    def request_package_name(self):
        """
            Get the package (dataset)
            for this resource
            by using revision_id
        """
        url = csv2rdf.config.config.ckan_api_url + '/rest/revision/' + self.revision_id
        r = requests.get(url, timeout=csv2rdf.config.config.ckan_request_timeout)
        assert r.ok, r
        revision = json.loads(r.content)
        return revision["packages"][0]

    def is_csv(self):
        if(re.search(r'csv', self.format, re.M | re.I)):
            return True
        else:
            return False

    def search_by_uri(self, uri):
        data = json.dumps({'id': self.id})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = csv2rdf.config.config.ckan_api_url + '/action/resource_search?query=url:'+str(uri)
        r = requests.post(url, timeout=csv2rdf.config.config.ckan_request_timeout, data=data, headers=headers)
        assert r.ok, r
        resource = json.loads(r.content)
        resource = resource["result"]["results"]
        try:
            resource = resource[0]
        except BaseException as e:
            logger.warning("No resource found with URI: %s"%uri)
            logger.warning("Exception occured %s"%str(e))
        return resource

    def get_metadata(self):
        """
            Resource has to be initialized
        """

        package_name = self.request_package_name()
        package = Package(package_name)
        package_metadata = package.get_metadata()

        model = RDF.Model()
        parser = RDF.Parser()
        parser.parse_string_into_model(model, package_metadata, "http://localhost/")

        output_model = RDF.Model()
        #title is label
        title_predicate = "http://purl.org/dc/terms/title"
        qs = RDF.Statement(subject = None, 
                           predicate = RDF.Node(uri_string = title_predicate), 
                           object = None)
        for statement in model.find_statements(qs): 
            statement.subject = RDF.Node(RDF.Uri("http://data.publicdata.eu/"+str(self.id)))
            statement.predicate = RDF.Node(RDF.Uri("http://www.w3.org/2000/01/rdf-schema#label"))
            output_model.add_statement(statement)
            break
        #description is comment
        description_predicate = "http://purl.org/dc/terms/description"
        qs = RDF.Statement(subject = None, 
                           predicate = RDF.Node(uri_string = description_predicate), 
                           object = None)
        for statement in model.find_statements(qs): 
            statement.subject = RDF.Node(RDF.Uri("http://data.publicdata.eu/"+str(self.id)))
            statement.predicate = RDF.Node(RDF.Uri("http://www.w3.org/2000/01/rdf-schema#comment"))
            output_model.add_statement(statement)
            break

        serializer = RDF.Serializer()
        return serializer.serialize_model_to_string(output_model)

    #
    # Interface methods - getters
    # Use these methods to get all the necessary info!
    #

    def get_ckan_url(self):
        return str(csv2rdf.config.config.ckan_base_url) + '/dataset/' + str(self.package_name) + '/resource/' + str(self.id)

    def get_wiki_url(self):
        return csv2rdf.config.config.wiki_base_url + '/wiki/' + csv2rdf.config.config.wiki_csv2rdf_namespace + self.id

if __name__ == '__main__':
    res = Resource('2625cb04-6a73-4154-9e22-bde490d5b61e')
    res.init()
    print res.get_metadata()
    pass
