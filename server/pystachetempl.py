import pystache

from config import config

class Index(object):
    def __init__(self):
        pass

class Csv2rdf(object):
    def __init__(self, resources):
        self.resources = resources
        
    def resources(self):
        return resources
    
    def item(self):
        items = []
        for resource in self.resources:
            print resource.ckan_url
            items.append({'ckan_url': resource.ckan_url,
                          'description': resource.description,
                          'wiki_url': resource.wiki_url,
                          'server_base_url': config.server_base_url,
                          'id': resource.id})
        return items
        
class RdfEdit(object):
    def __init__(self, resource, mapping_name):
        self.resource = resource
        self.rdf_file_url = config.server_base_url + 'sparqlified/' + resource.id + "_" + mapping_name + ".rdf"
    
    def item(self):
        items = []
        items.append({'ckan_url': self.resource.ckan_url,
                      'description': self.resource.description,
                      'wiki_url': self.resource.wiki_url,
                      'server_base_url': config.server_base_url,
                      'id': self.resource.id,
                      'rdf_file_url': self.rdf_file_url})
        return items
    
if __name__ == '__main__':
    entityName = "ambulance-call-outs-to-animal-attack-incidents"
    index = Index(entityName)
    
    renderer = pystache.Renderer(search_dirs="templates/")
    print renderer.render(index)
    pass
