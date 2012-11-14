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
    def rdfEdit(self, resourceId, configName):
        ckan = CkanInterface()
        entityName = ckan.getResourcePackage(resourceId)
        entity = ckan.getEntity(entityName)
        resourceDescription = ckan.getResourceKey(entityName, resourceId, 'description')
        
        #convert CSV to RDF
        self._processResource(entityName, resourceId, configName)
        
        rdfEdit = pystachetempl.RdfEdit(entityName, resourceId, resourceDescription, configName)
        return self.renderer.render(rdfEdit)
        #TODO: make page with the editor!
        
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