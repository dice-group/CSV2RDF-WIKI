#
# Server interface - views here
#
import cherrypy
from ckaninterface import CkanInterface
import pystache
import pystachetempl
import ckanconfig
from wikitoolsinterface import WikiToolsInterface
from subprocess import Popen
from subprocess import PIPE
from os import path

class CSV2RDFApp(object):
    def __init__(self,base_location=None, api_key=None):
        self.base_location = base_location
        self.api_key = api_key
        self.renderer = pystache.Renderer(search_dirs="static/templates/")
        
    @cherrypy.expose
    def index(self):
        index = pystachetempl.Index()
        return self.renderer.render(index)
        
    @cherrypy.expose
    def processResource(self, entityName, resourceUrl):
        # get resource from the URL
        ckan = CkanInterface()
        sparqlify = "../lib/sparqlify/sparqlify.jar"
        csvfile = ckan.downloadResource(entityName,resourceUrl)
        wiki = WikiToolsInterface()
        configfile = 'sparqlify-mappings/' + entityName + '/'  + wiki.getResourceConfiguration(entityName, resourceUrl)
        print path.abspath(csvfile)
        print path.abspath(configfile)
        print path.abspath(sparqlify)
        if(csvfile and configfile):
            sparqlify = Popen(["java", "-cp", sparqlify, "org.aksw.sparqlify.csv.CsvMapperCliMain", "-f", csvfile, "-c", configfile], stdout=PIPE)
            output = sparqlify.communicate()[0]
            return output
        else:
            return "something went wrong"    
        #Save to file?
        #csvfile = "files/"+entityName+"/"+filename
        #read configuration from the wiki and save to the 
        #configfile = "sparqlify-mappings/"+entityName+" "+filename+".sparqlify"
        #print retcode
        
    def showEntity(self, entityName):
        ckan = CkanInterface(base_location=self.base_location, api_key=self.api_key)
        entity = ckan.getEntity(entityName)
        return ckan.pFormat(entity)
        
if __name__ == '__main__':
    publicdataeu = CSV2RDFApp(base_location=ckanconfig.base_location, api_key=ckanconfig.api_key)
    cherrypy.quickstart(publicdataeu, '/', 'csv2rdf.cherrypy.config')
    cherrypy.config.update('cherrypy.config')