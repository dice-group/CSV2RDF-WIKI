from wikitools import wiki
from wikitools import api
import wikiconfig

class WikiToolsInterface:
    def __init__(self, api_url="http://wiki.publicdata.eu/api.php"):
        #init wikitools
        self.site = wiki.Wiki(api_url)
        #login with the data from wikiconfig.py
        self.site.login(wikiconfig.username, password=wikiconfig.password)
        self.site.setMaxlag = -1 #will wait forever
        
    def getPageContent(self, entityName):
        params = {'action':'query', 'prop':'revisions', 'rvprop':'content', 'titles':entityName}
        request = api.APIRequest(self.site, params)
        result = request.query()
        pages = result['query']['pages']
        for pageid in pages:
            page = pages[pageid]
            #get the last revision
            return page['revisions'][0]["*"]
            
    def getResourceConfiguration(self, entityName, resourceUrl):
        pageContent = self.getPageContent(entityName)
        resourceConfig = self._extractConfig(pageContent, resourceUrl)
        filename = self._saveConfigToFile(entityName, resourceUrl, resourceConfig)
        return filename
    
    def _extractConfig(self, pageContent, resourceUrl):
        #strip nowiki tag
        import re
        output = re.sub(r'(<.*nowiki>)', r'', pageContent)
        return output
    
    def _saveConfigToFile(self, entityName, resourceUrl, resourceConfig):
        from database import Database
        import os
        newpath = 'sparqlify-mappings/'+entityName+'/'
        db = Database(newpath)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        #get entity
        from ckaninterface import CkanInterface
        ckan = CkanInterface()
        resourceId = ckan.getResourceId(entityName, resourceUrl)
        filename = resourceId + '.sparqlify'
        db.saveDbaseRaw(filename, resourceConfig)
        return filename

if __name__ == '__main__':
    wt = WikiToolsInterface()
    entityName = 'staff-organograms-and-pay-joint-nature-conservation-committee'
    resourceUrl = 'http://data.defra.gov.uk/ops/jncc/Jncc+government-staff-and-salary-data-blank-template---March-2011-senior-data.csv'
    print wt.getResourceConfiguration(entityName, resourceUrl)