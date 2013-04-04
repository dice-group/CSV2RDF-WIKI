import re

import json
import pdb
import requests

import config
from interfaces import AuxilaryInterface


class Resource(AuxilaryInterface):
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
        url = config.ckan_api_url + '/action/resource_show'
        r = requests.post(url, timeout=config.ckan_request_timeout, data=data, headers=headers)
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
        url = config.ckan_api_url + '/rest/revision/' + self.revision_id
        r = requests.get(url, timeout=config.ckan_request_timeout)
        assert r.ok, r
        revision = json.loads(r.content)
        return revision["packages"][0]

    def is_csv(self):
        if(re.search(r'csv', self.format, re.M | re.I)):
            return True
        else:
            return False

    #
    # Interface methods - getters
    # Use these methods to get all the necessary info!
    #

    def get_ckan_url(self):
        return str(config.ckan_base_url) + '/dataset/' + str(self.package_name) + '/resource/' + str(self.id)

    def get_wiki_url(self):
        return config.wiki_base_url + '/wiki/' + config.wiki_csv2rdf_namespace + self.id

if __name__ == '__main__':
    res = Resource('1aa9c015-3c65-4385-8d34-60ca0a875728')
    pdb.set_trace() ############################## Breakpoint ##############################
    res.init()
    print res.is_csv()
    pass
