import config
from ckanclient import CkanClient
from interfaces import AuxilaryInterface
import requests
from database import Database

class Package(AuxilaryInterface):
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
        self.ckan = CkanClient(base_location=config.ckan_api_url,
                               api_key=config.ckan_api_key)
        self.initialize()
        
    def initialize(self):
        entity = self.ckan.package_entity_get(self.name)
        self.unpack_object_to_self(entity)
        
    def download_all_resources(self):
        """
            Overwrites existing files!
        """
        db = Database(config.resource_dir)
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
    print package.resources
