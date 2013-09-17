#
# Server interface - views here
#
import cherrypy
import json
import pystache
import logging

import csv2rdf.config
import csv2rdf.server.pystachetempl
import csv2rdf.ckan.application
import csv2rdf.ckan.resource
import csv2rdf.tabular.sparqlify


class CSV2RDFApp(object):
    def __init__(self):
        self.renderer = pystache.Renderer(search_dirs="csv2rdf/server/static/templates/")
        
    @cherrypy.expose(alias='index.html')
    def index(self):
        index = csv2rdf.server.pystachetempl.Index()
        return self.renderer.render(index)
        
    @cherrypy.expose(alias='csv2rdf.html')
    def csv2rdf(self):
        #read several resource, give navigation link to wiki and CKAN
        #let transform each of them
        res1 = csv2rdf.ckan.resource.Resource('676e2f9b-c05f-4fd5-844a-25497c3c2c9e')
        res2 = csv2rdf.ckan.resource.Resource('6023100d-1c76-4bee-9429-105caa061b9f')
        res3 = csv2rdf.ckan.resource.Resource('1aa9c015-3c65-4385-8d34-60ca0a875728')
        resources = [res1, res2, res3]
        map(lambda x: x.init(), resources)
        page = csv2rdf.server.pystachetempl.Csv2rdf(resources)
        return self.renderer.render(page)

    @cherrypy.expose(alias="rdf_edit.html")
    def rdf_edit(self, resource_id, configuration_name='default-tranformation-configuration'):
        mapping_name = configuration_name 
        resource_id = resource_id.lower()
        
        resource = csv2rdf.ckan.resource.Resource(resource_id)
        resource.init()
        sparqlify = csv2rdf.tabular.sparqlify.Sparqlify(resource_id)
        
        if(sparqlify.transform_resource_to_rdf(mapping_name)):
            logging.info("The resource %s %s was sent to the queue." % (resource_id, mapping_name))
            
            rdf_edit = csv2rdf.server.pystachetempl.RdfEdit(resource, mapping_name)
            return self.renderer.render(rdf_edit)
        else:
            return self.renderer.render(rdf_edit)

        
    ####### AJAX calls
    
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

    @cherrypy.expose    
    def getUriByCkanResourceId(self, resource_id):
        resource = csv2rdf.ckan.resource.Resource(resource_id)
        resource.init() 
        return json.dumps(resource.url)
    
    @cherrypy.expose        
    def get_exposed_rdf_list(self):
        ckan = csv2rdf.ckan.application.CkanApplication()
        return json.dumps(ckan.get_sparqlified_list())
        
    def _get_black_list(self):
        f = open('files_over_50MB', 'rU')
        black_list = f.read()
        f.close()
        return black_list.split('\n')
        
if __name__ == '__main__':
    publicdataeu = CSV2RDFApp()
    cherrypy.quickstart(publicdataeu, '/', 'csv2rdf/server/config')
    cherrypy.config.update('server/config')

def application(environ, start_response): 
    cherrypy.tree.mount(CSV2RDFApp(), '/', 'csv2rdf/server/config')
    return cherrypy.tree(environ, start_response)
