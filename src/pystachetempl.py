import pystache

class Index(object):
    def __init__(self):
        pass

class Csv2rdf(object):
    def __init__(self):
        pass
    
class RdfEdit(object):
    def __init__(self, entityName, resourceId, resourceDescription):
        self.entityName = entityName
        self.resourceId = resourceId
        self.resourceDescription = resourceDescription
    
    def entityName(self):
        return self.entityName
    
    def resourceId(self):
        return self.resourceId
    
    def resourceDescription(self):
        return self.resourceDescription
        
if __name__ == '__main__':
    entityName = "ambulance-call-outs-to-animal-attack-incidents"
    index = Index(entityName)
    
    renderer = pystache.Renderer(search_dirs="templates/")
    print renderer.render(index)
    pass