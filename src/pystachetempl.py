import pystache

class Index(object):
    def __init__(self , entityName):
        from ckaninterface import CkanInterface
        ckan = CkanInterface()
        self.entity = ckan.getEntity(entityName)
        print self.entity
        
if __name__ == '__main__':
    entityName = "ambulance-call-outs-to-animal-attack-incidents"
    index = Index(entityName)
    
    renderer = pystache.Renderer(search_dirs="templates/")
    print renderer.render(index)
    pass