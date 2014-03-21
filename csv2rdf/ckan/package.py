import requests
from ckanclient import CkanClient

import csv2rdf.config.config
import csv2rdf.database
import csv2rdf.interfaces


class Package(csv2rdf.interfaces.AuxilaryInterface):
    """ Reflects the CKAN package.
        CKAN package contains one or several CKAN resources
        Properties:
            maintainer, package_name, maintainer_email, 
            id, metadata_created, ckan, relationships,
            metadata_modified, author, author_email, 
            download_url, state, version, license_id, type,
            resources: [], tags: [], tracking_summary, name,
            isopen, license, notes_rendered, url, ckan_url,
            notes, license_title, ratings_average,
            extras: {geographic_coverage, temporal_coverage-from,
            temporal_granularity, date_updated, published_via,
            mandate, precision, geographic_granularity,
            published_by, taxonomy_url, update_frequency,
            temporal_coverage-to, date_update_future, date_released},
            license_url, ratings_count, title, revision_id
            
            ckan - <ckanclient.CkanClient object at 0x972ac8c>
    """
    def __init__(self, package_name):
        self.name = package_name
        self.ckan = CkanClient(base_location=csv2rdf.config.config.ckan_api_url,
                               api_key=csv2rdf.config.config.ckan_api_key)
        self.initialize()
        
    def initialize(self):
        entity = self.ckan.package_entity_get(self.name)
        self.unpack_object_to_self(entity)

    def get_metadata(self, dataset=None):
        if(dataset is None):
            dataset = self.name

        dataset_meta = self.cache_metadata_get(dataset)
        if(not dataset_meta):
            url = csv2rdf.config.config.ckan_base_url + "/dataset/"+dataset+".rdf"
            r = requests.get(url)
            assert r.status_code == requests.codes.ok #is 200?
            dataset_meta = r.content
            self.cache_metadata_put(dataset, dataset_meta)
        return dataset_meta

    def cache_metadata_get(self, dataset):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_packages_metadata_path)
        if db.is_exists(dataset):
            return db.loadDbase(dataset)
        else:
            return False

    def cache_metadata_put(self, dataset, metadata):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.data_packages_metadata_path)
        db.saveDbase(dataset, metadata)
        
    def download_all_resources(self):
        """
            Overwrites existing files!
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resource_dir)
        for resource in self.resources:
            url = resource['url']
            filename = self.extract_filename_url(url)
            try:
                r = requests.get(url, timeout=self.timeout)
                db.saveDbaseRaw(filename, r.content)
            except BaseException as e:
                print "Could not get the resource " + str(resource['id']) + " ! " + str(e)
        
    #
    # Interface - getters
    #
        
    def get_ckan_url(self):
        return str(self.ckan_base_url) + '/dataset/' + str(self.name)
        
if __name__ == '__main__':
    package = Package('financial-transactions-data-ago-cps')
    #print package.resources
    print package.get_metadata()
