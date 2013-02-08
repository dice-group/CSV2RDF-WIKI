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
        self.ckan = CkanClient(base_location=ckanconfig.api_url,
                               api_key=ckanconfig.api_key)
        self.initialize()
        
    def initialize(self):
        entity = self.ckan.package_entity_get(self.name)
        for key in entity:
            setattr(self, key, entity[key])
    
    def download_all_resources(self):
        db = Database(self.resource_dir)
        for resource in self.resources:
            url = resource['url']
            filename = self.extract_filename_url(url)
            try:
                r = requests.get(url, timeout=self.timeout)
                db.saveDbaseRaw(filename, r.content)
            except BaseException as e:
                print "Could not get the resource " + str(resource['id']) + " ! " + str(e)
            
    def is_resource_csv(self, resource):
        if(re.search( r'csv', resource['format'], re.M|re.I)):
            return True
        else:
            return False
    
    #
    # Interface - getters
    #
        
    def get_ckan_url(self):
        return str(self.ckan_base_url) + '/dataset/' + str(self.name)