from wikitools import wiki
from wikitools import api
from prefixcc import PrefixCC
import wikiconfig

class WikiToolsInterface:
    def __init__(self, api_url="http://wiki.publicdata.eu/api.php"):
        #init wikitools
        self.site = wiki.Wiki(api_url)
        #login with the data from wikiconfig.py
        self.site.login(wikiconfig.username, password=wikiconfig.password)
        self.site.setMaxlag = -1 #will wait forever
        
    def getPageContent(self, resourceId):
        namespace = 'Csv2rdf:'
        title = namespace + resourceId
        params = {'action':'query', 'prop':'revisions', 'rvprop':'content', 'titles':title}
        request = api.APIRequest(self.site, params)
        result = request.query()
        pages = result['query']['pages']
        try:
            for pageid in pages:
                page = pages[pageid]
                #get the last revision
                return page['revisions'][0]["*"]
        except:
            #Config does not exist
            return False
            
    def getResourceConfiguration(self, entityName, resourceId):
        
        from ckaninterface import CkanInterface
        ckan = CkanInterface()
        resourceUrl = ckan.getResourceUrl(entityName, resourceId)
                
        pageContent = self.getPageContent(resourceId)
        if(pageContent):
            resourceConfigs = self._extractConfig(pageContent)
            sparqlifyConfig = self._convertToSparqlifyML(resourceConfigs)
            filename = self._saveConfigToFile(entityName, resourceId, sparqlifyConfig)
            return filename
        else:
            return False
    
    def _extractConfig(self, pageContent):
        import re
        lines = pageContent.split('\n')
        configs = []
        for line in lines:
            if(re.match('^{{', line)):
                inside_config = True
                config = {}
                config['type'] = line[2:] #'RelCSV2RDF|'
                config['type'] = config['type'][:-1] # 'RelCSV2RDF'
                continue
            
            if(re.match('^}}', line)):
                #push config to the configs
                configs.append(config)
                del config
                inside_config = False
                continue
            
            if(inside_config):
                prop = line.split('=')[0]
                value = str(line.split('=')[1])
                prop = prop.strip()
                value = ' '.join(value[:-1].split())
                config[prop] = value        
        return configs
    
    def _convertToSparqlifyML(self, resourceConfigs):
        import re
        print resourceConfigs
        csv2rdfconfig = ''
        prefixcc = PrefixCC()
        #scan all colX values and extract prefixes
        prefixes = []
        properties = {} #properties['col1'] = id >>>> ?obs myprefix:id ?col1
        for config in resourceConfigs:
            if(config['type'] == 'RelCSV2RDF'):
                for key in config.keys():
                    if(re.match('^col', key)):
                        prefixes += prefixcc.extractPrefixes(config[key])
                        properties[key] = config[key]
        #remove duplicates from prefixes
        prefixes = dict.fromkeys(prefixes).keys()
        #inject qb prefix
        prefixes += ['qb']
        for prefix in prefixes:
            csv2rdfconfig += prefixcc.getSparqlifyNamespace(prefix) + "\n"
        #Add custom prefix to non-prefixed values
        csv2rdfconfig += "Prefix publicdata:<http://wiki.publicdata.eu/ontology/>" + "\n"
        #Add fn sparqlify prefix
        csv2rdfconfig += "Prefix fn:<http://aksw.org/sparqlify/>" + "\n"
        
        csv2rdfconfig += "Create View Template DefaultView As" + "\n"
        csv2rdfconfig += "  CONSTRUCT {" + "\n"
        csv2rdfconfig += "      ?obs a qb:Observation ." + "\n"
        
        for prop in properties:
            csv2rdfconfig += "      ?obs "+ self._extractProp(properties[prop]) +" ?"+ prop + " .\n"
        print properties
        csv2rdfconfig += "  }" + "\n"
        csv2rdfconfig += "  With" + "\n"
        #TODO: Check Claus e-mail and fix it!!! fn:rowId()
        csv2rdfconfig += "      ?obs = uri(concat('http://wiki.publicdata.eu/observation', ''))" + "\n"
        for prop in properties:
            csv2rdfconfig += "      ?" + prop + " = " + self._extractType(properties[prop], prop) + "\n"
        
        return csv2rdfconfig
    
    def _extractProp(self, wikiString):
        prop = wikiString.split('->')[0]
        if(len(prop.split(':')) == 1):
            return "publicdata:"+prop
        else:
            return prop
    
    def _extractType(self, wikiString, column):
        column_number = column[3:]
        try:
            t = wikiString.split('->')[1]
            t = t.split('^^')[0]
            return "typedLiteral(?"+column_number+", "+t+")"
        except:
            return "plainLiteral(?"+column_number+")"
    
    def _saveConfigToFile(self, entityName, resourceId, resourceConfig):
        from database import Database
        import os
        newpath = 'sparqlify-mappings/'
        db = Database(newpath)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        #get entity        
        filename = str(resourceId) + '.sparqlify'
        db.saveDbaseRaw(filename, resourceConfig)
        return newpath + filename

if __name__ == '__main__':
    wt = WikiToolsInterface()
    entityName = 'staff-organograms-and-pay-joint-nature-conservation-committee'
    resourceId = '6023100d-1c76-4bee-9429-105caa061b9f'
    print wt.getResourceConfiguration(entityName, resourceId)