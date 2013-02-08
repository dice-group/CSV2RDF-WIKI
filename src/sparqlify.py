class Sparqlify():
    def __init__(self):
        pass
    
    def transform_resource_to_rdf(self, resource_id, configuration_name):
        sparqlify_call = ["java",
                          "-cp", self.sparqlify_jar,
                          "org.aksw.sparqlify.csv.CsvMapperCliMain",
                          "-f", self.get_csv_file_path(),
                          "-c", self.get_sparqlify_configuration_path(configuration_name),
                          "-d", self.mappings[configuration_name]['delimiter']]
        
        print str(' '.join(sparqlify_call))
    
        rdf_filename = self.rdf_files_path + self.id + '_' + configuration_name + '.rdf'
        f = open(rdf_filename, 'w')
        pipe = subprocess.Popen(sparqlify_call, shell=True, stdout=f, stderr=subprocess.PIPE)
        sparqlify_message = pipe.stderr.read()
        pipe.stderr.close()
        f.close()
        
        return sparqlify_message, pipe.returncode
    
    def get_rdf_path(self, configuration_name):
        if(os.path.exists(self.rdf_files_path + self.id + '_' + configuration_name + '.rdf')):
            return self.rdf_files_path + self.id + '_' + configuration_name + '.rdf'
        else:
            self.transform_to_rdf(configuration_name)
            return self.rdf_files_path + self.id + '_' + configuration_name + '.rdf'
        
    def get_rdf_url(self, configuration_name):
        return self.server_base_url + self.get_rdf_file_path(configuration_name)