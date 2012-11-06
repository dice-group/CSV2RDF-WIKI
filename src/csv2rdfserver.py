#
# Server interface - views here
#
import cherrypy
import json
from ckaninterface import CkanInterface
import pystache
import pystachetempl
from wikitoolsinterface import WikiToolsInterface
from subprocess import Popen
from subprocess import PIPE
from os import path
import os

class CSV2RDFApp(object):
    def __init__(self):
        self.renderer = pystache.Renderer(search_dirs="static/templates/")
        
    @cherrypy.expose(alias='index.html')
    def index(self):
        index = pystachetempl.Index()
        return self.renderer.render(index)
    
    @cherrypy.expose(alias='csv2rdf.html')
    def csv2rdf(self):
        csv2rdf = pystachetempl.Csv2rdf()
        return self.renderer.render(csv2rdf)

    @cherrypy.expose(alias="rdfedit.html")
    def rdfEdit(self, entityName, resourceId):
        ckan = CkanInterface()
        entity = ckan.getEntity(entityName)
        resourceDescription = ckan.getResourceKey(entityName, resourceId, 'description')
        
        rdfEdit = pystachetempl.RdfEdit(entityName, resourceId, resourceDescription)
        return self.renderer.render(rdfEdit)
        #TODO: make page with the editor!

    @cherrypy.expose
    def processResource(self, entityName, resourceId):
        # get resource from the URL
        ckan = CkanInterface()
        sparqlify = "../lib/sparqlify/sparqlify.jar"
        csvfile = ckan.downloadResource(entityName,resourceId)
        wiki = WikiToolsInterface()
        configfile = wiki.getResourceConfiguration(entityName, resourceId)
        print configfile
        rdfoutputpath = 'sparqlified/'+entityName+'/'
        if not os.path.exists(rdfoutputpath):
            os.makedirs(rdfoutputpath)
        rdfoutput = rdfoutputpath+resourceId+'.rdf'
        
        if(csvfile and configfile):
            print ' '.join(["java", "-cp", sparqlify, "org.aksw.sparqlify.csv.CsvMapperCliMain", "-f", csvfile, "-c", configfile, ">", rdfoutput])
            f = open(rdfoutput, 'w')
            Popen(["java", "-cp", sparqlify, "org.aksw.sparqlify.csv.CsvMapperCliMain", "-f", csvfile, "-c", configfile], stdout=f)
            f.close()
            return json.dumps(rdfoutput)
        else:
            return ''    
        #Save to file?
        #csvfile = "files/"+entityName+"/"+filename
        #read configuration from the wiki and save to the 
        #configfile = "sparqlify-mappings/"+entityName+" "+filename+".sparqlify"
        #print retcode
        
    def showEntity(self, entityName):
        ckan = CkanInterface()
        entity = ckan.getEntity(entityName)
        return ckan.pFormat(entity)
        
    ####### AJAX calls
    
    @cherrypy.expose
    def getCKANEntity(self, entityName):
        ckan = CkanInterface()
        entity = ckan.getEntity(entityName)
        cherrypy.response.headers['Content-Type'] = "application/json"
        return json.dumps(entity)
    
    @cherrypy.expose    
    def getSparqlifiedResourceNLines(self, entityName, resourceId, n):
        n = int(n)
        rdfoutputpath = 'sparqlified/'+entityName+'/'
        rdfoutput = rdfoutputpath+resourceId+'.rdf'
        print rdfoutput
        try:
            with open(rdfoutput, 'r') as rdffile:
                head=[rdffile.next() for x in xrange(n)]
            return json.dumps(head)
        except:
            return json.dumps('')
        
if __name__ == '__main__':
    publicdataeu = CSV2RDFApp()
    cherrypy.quickstart(publicdataeu, '/', 'csv2rdf.cherrypy.config')
    cherrypy.config.update('cherrypy.config')