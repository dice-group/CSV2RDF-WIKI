#
# Server interface - views here
#
import cherrypy
from ckaninterface import CkanInterface
import pystache
import pystachetempl

class CSV2RDFApp(object):
    def __init__(self,base_location=None, api_key=None):
        self.base_location = base_location
        self.api_key = api_key
        self.renderer = pystache.Renderer(search_dirs="templates/")
        
    @cherrypy.expose
    def index(self, entityName):
        #http://localhost:8090/?entityName=staff-organograms-and-pay-joint-nature-conservation-committee
        index = pystachetempl.Index(entityName)
        self.entityName = entityName
        return self.renderer.render(index)
    
    @cherrypy.expose
    def processResource(self, resource):
        return resource + ' ' + self.entityName
    
    def showEntity(self, entityName):
        ckan = CkanInterface(base_location=self.base_location, api_key=self.api_key)
        entity = ckan.getEntity(entityName)
        return ckan.pFormat(entity)
        
if __name__ == '__main__':
    publicdataeu = CSV2RDFApp(base_location='http://publicdata.eu/api', api_key='e7a928be-a3e8-4a34-b25e-ef641045bbaf')
    cherrypy.config.update('cherrypy.config')
    cherrypy.quickstart(publicdataeu, '/')