from wikitools import wiki
from wikitools import api
import wikitools
from prefixcc import PrefixCC
import wikiconfig

class WikiToolsInterface:
    def __init__(self, api_url="http://wiki.publicdata.eu/api.php"):
        #init wikitools
        self.site = wiki.Wiki(api_url)
        #login with the data from wikiconfig.py
        self.site.login(wikiconfig.username, password=wikiconfig.password)
        self.site.setMaxlag = -1 #will wait forever
        self.csvHeaderThreshold = 0.2
        self.namespace = 'Csv2rdf:'
    
    def createPage(self, resourceId, text):
        title = self.namespace + resourceId
        page = wikitools.Page(self.site, title=title)
        page.edit(text=text)
        return True
    
    def extractCSVHeader(self, csv):
        for position, line in enumerate(csv):
            items = line.split(',')
            overall = len(items)
            empty = 0
            for item in items:
                if(item == ''):
                    empty = empty + 1
            
            if(float(empty) / float(overall) < self.csvHeaderThreshold):
                return (position, line)
        return ''
        
    def generateDefaultPageForResource(self, resourceId):
        #getting necessary info
        from ckaninterface import CkanInterface
        ckan = CkanInterface()
        entityName = ckan.getResourcePackage(resourceId)
        resourceDescription = ckan.getResourceKey(entityName, resourceId, 'description')
        
        page = '{{CSV2RDFHeader}} \n'
        page += '\n'
        
        #link to the publicdata.eu dataset
        wikilink = '[http://publicdata.eu/dataset/'+entityName+'/resource/'+resourceId+' "'+resourceDescription+'" resource]'
        page += 'This configuration is used to transform '+wikilink+' to RDF. \n'
        page += '\n'
        
        #get the header from the csv file
        from database import Database
        db = Database('')
        csv = db.loadResourceCSV(resourceId, n=15)
        (headerPosition, header) = self.extractCSVHeader(csv)
        #TODO: test different threshold values
        
        #CSV2RDF Template
        page += '{{RelCSV2RDF|\n'
        page += 'name = default tranformation configuration |\n'
        page += 'header = '+str(headerPosition)+' |\n'
        page += 'omitRows = -1 |\n'
        page += 'omitCols = -1 |\n'
        
        #Split header and create column definition
        i = 1
        for item in header.split(','):
            page += 'col'+str(i)+' = '+str(''.join(item.split()))+' |\n'
            i = i + 1
        
        #Close template
        page += '}}\n'
        page += '\n'
                
        return page
        
    def getPageContent(self, resourceId):
        title = self.namespace + resourceId
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
            sparqlifyConfig = self._convertToSparqlifyML(resourceConfigs, resourceId)
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
    
    def _convertToSparqlifyML(self, resourceConfigs, resourceId):
        import re
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
        csv2rdfconfig += "  }" + "\n"
        csv2rdfconfig += "  With" + "\n"
        #TODO: Check Claus e-mail and fix it!!! fn:rowId()
        csv2rdfconfig += "      ?obs = uri(concat('http://data.publicdata.eu/"+resourceId+"#', ?rowId))" + "\n"
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
    resourceId = '6023100d-1c76-4bee-9429-105caa061b9f' #Okay header here
    resourceId = '0967cb11-4384-425a-8565-94ed36a514df' #big bad header
    #wt.createPage("00000000-0000-0000-0000-000000000000")
    #print wt.createDefaultPageForResource(resourceId)
    #print wt.getResourceConfiguration(entityName, resourceId)