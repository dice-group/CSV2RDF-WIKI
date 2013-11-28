import csv2rdf.config

class RdfEditTemplate(object):
    def __init__(self, resource, mapping_name):
        self.resource = resource
        self.rdf_file_url = csv2rdf.config.config.server_base_url + 'sparqlified/' + resource.id + "_" + mapping_name + ".rdf"

    def item(self):
        items = []
        items.append({'ckan_url': self.resource.ckan_url,
                      'description': self.resource.description,
                      'wiki_url': self.resource.wiki_url,
                      'server_base_url': csv2rdf.config.config.server_base_url,
                      'id': self.resource.id,
                      'rdf_file_url': self.rdf_file_url})
        return items
