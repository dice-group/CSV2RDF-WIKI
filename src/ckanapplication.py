class CKANApplication(AuxilaryInterface):
    """ Reflects the CKAN application itself,
        interfaces for getting packages etc.
    """
    def __init__(self):
        self.ckan = CkanClient(base_location=ckanconfig.api_url,
                               api_key=ckanconfig.api_key)
        self.csv_resource_list_filename = 'csv_resource_list'
        
    def update_csv_resource_list(self):
        output = []
        package_list = self.get_package_list()
        
        for package in package_list:
            entity = Package(package)
            for resource in entity['resources']:
                if(self.isCSV(resource)):
                    output.append(resource['id'])
        
        db = Database()
        db.saveDbase(self.csv_resource_list_filename, output)
        
    def get_package_list(self):
        return self.ckan.package_list()
        
    def get_csv_resource_list(self):
        db = Database()
        return db.loadDbase(self.csv_resource_list_filename)
        
    def get_sparqlified_list(self):
        return os.listdir(self.rdf_files_exposed_path)
        
    def update_sparqlified_list(self):
        #update list - make soft links to the files
        rdf_files = os.listdir(self.rdf_files_path)
        for rdf_file in rdf_files:
            #make a soft link
            link_to = os.path.abspath(self.rdf_files_path + rdf_file)
            resource_id = rdf_file[:36] #take resource_id part only
            link = self.rdf_files_exposed_path + resource_id
            make_soft_link = ["ln",
                              "-f",
                              "-s",
                              link_to,
                              link]
            pipe = subprocess.Popen(make_soft_link, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            print pipe_message