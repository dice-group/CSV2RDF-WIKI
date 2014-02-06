import csv2rdf.config

class Csv2rdfTemplate(object):
    def __init__(self, resources):
        self.resources = resources

    def resources(self):
        return self.resources

    def item(self):
        items = []
        for resource in self.resources:
            print resource.ckan_url
            items.append({'ckan_url': resource.ckan_url,
                          'description': resource.description,
                          'wiki_url': resource.wiki_url,
                          'server_base_url': csv2rdf.config.config.server_base_url,
                          'id': resource.id})
        return items
