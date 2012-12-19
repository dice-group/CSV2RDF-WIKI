#
# Server interface - views here
#
import cherrypy
import json
import ckaninterface
import pystache
import pystachetempl

class CSV2RDFApp(object):
    def __init__(self):
        self.renderer = pystache.Renderer(search_dirs="static/templates/")
        
    @cherrypy.expose(alias='index.html')
    def index(self):
        index = pystachetempl.Index()
        return self.renderer.render(index)
    
    @cherrypy.expose(alias='csv2rdf.html')
    def csv2rdf(self):
        #read several resource, give navigation link to wiki and CKAN
        #let transform each of them
        res1 = ckaninterface.Resource('676e2f9b-c05f-4fd5-844a-25497c3c2c9e')
        res2 = ckaninterface.Resource('6023100d-1c76-4bee-9429-105caa061b9f')
        resources = [res1, res2]
        csv2rdf = pystachetempl.Csv2rdf(resources)
        return self.renderer.render(csv2rdf)

    @cherrypy.expose(alias="rdf_edit.html")
    def rdf_edit(self, resource_id, configuration_name='default-tranformation-configuration'):
        
        resource = ckaninterface.Resource(resource_id)
        rdf_file_url = resource.get_rdf_file_url(configuration_name)
        rdf_edit = pystachetempl.RdfEdit(resource, rdf_file_url)
        return self.renderer.render(rdf_edit)
        #TODO: make page with the editor!
        
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
    def get_exposed_rdf_list(self):
        ckan = ckaninterface.CKAN_Application()
        return json.dumps(ckan.get_sparqlified_list())
        
if __name__ == '__main__':
    publicdataeu = CSV2RDFApp()
    cherrypy.quickstart(publicdataeu, '/', 'csv2rdf.cherrypy.config')
    cherrypy.config.update('cherrypy.config')