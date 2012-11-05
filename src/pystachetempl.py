import pystache

class Index(object):
    def __init__(self):
        pass

class Csv2rdf(object):
    def __init__(self):
        pass
        
if __name__ == '__main__':
    entityName = "ambulance-call-outs-to-animal-attack-incidents"
    index = Index(entityName)
    
    renderer = pystache.Renderer(search_dirs="templates/")
    print renderer.render(index)
    pass