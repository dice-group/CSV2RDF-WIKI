from ckanclient import CkanClient
import wikitools
from database import Database
import requests
import os
from unidecode import unidecode
import re
import urllib2
from prefixcc import PrefixCC

#Configs
import ckanconfig
import csv2rdfconfig
import wikiconfig
import sparqlifyconfig

import json
requests.defaults.danger_mode = True

#
# CKAN scripting
#

class CkanInterface:
    def __init__(self, base_location=ckanconfig.api_url, api_key=ckanconfig.api_key):
        self.base_location = base_location
        self.api_key = api_key
        self.ckan = ckanclient.CkanClient(base_location=base_location,
                                          api_key=api_key)
        self.db = Database('data/')
        self.errorlog = open('error.log', 'a+')
        self.log = open('log.log', 'a+')
        self.errorlogfile = 'error.log'
        self.logfile = 'log.log'
    
    def getEntityFiles(self, entityName):
        import os
        from subprocess import call
        filelist = os.listdir("files/"+entityName)
        for filename in filelist:
            print os.getcwd()
            sparqlify = "../lib/sparqlify/sparqlify.jar"
            csvfile = "files/"+entityName+"/"+filename
            print csvfile
            configfile = "sparqlify-mappings/"+entityName+" "+filename+".sparqlify"
            retcode = call(["java", "-cp", sparqlify, "org.aksw.sparqlify.csv.CsvMapperCliMain", "-f", csvfile, "-c", configfile])
            print retcode
        pass
    
    def pFormat(self, object):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(object)
            
    def getPackageList(self):
        try:
            package_list = self.db.loadDbase("package_list")
        except IOError as error:
            print "I/O error({0}): {1}".format(error.errno, error.strerror)
            print "Creating new package list"
            package_list = self.ckan.package_register_get()
            self.db.saveDbase("package_list", package_list)
        return package_list
    
    def isCSV(self, resource):
        import re
        if(re.search( r'csv', resource['format'], re.M|re.I)):
            return True
        else:
            return False
    
    def rewriteEntity(self, entity):
        entityName = entity['name']
        newpath = 'files/'+entityName+'/'
        self.filesdb = Database(newpath)
        for resource in entity['resources']:
            url = resource['url']
            filename = url.split('/')[-1].split('#')[0].split('?')[0]
            try:
                resource = self.filesdb.loadDbase(filename)
                self.filesdb.saveDbaseRaw(filename, resource)
            except:
                pass
       
    def downloadEntityResources(self, entity):
        entityName = entity['name']
        newpath = 'files/'+entityName+'/'
        self.filesdb = Database(newpath)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        for resource in entity['resources']:
            print resource['url'].encode('utf-8')
            url = resource['url']
            filename = url.split('/')[-1].split('#')[0].split('?')[0]
            try:
                resource = self.filesdb.loadDbase(filename)
                self.log.write(entityName.encode('utf-8') + ' ' + url.encode('utf-8') + ' readed from HDD\n')
                self.log.flush()
            except IOError as error:
                print "I/O error({0}): {1}".format(error.errno, error.strerror)
                print "Creating new folder"
                print "Fetching resource from URI"
                try:
                    r = requests.get(url, timeout=100)
                    self.filesdb.saveDBaseRaw(filename, r.content)
                    self.log.write(entityName.encode('utf-8') + ' ' + url.encode('utf-8') + ' OK!\n')
                    self.log.flush()
                except Exception as e:
                    self.errorlog.write(entityName.encode('utf-8') + ' ' + url.encode('utf-8') + ' ' + str(e) + '\n')
                    self.errorlog.flush()
    
    def getCSVResourceList(self):
        output = []
        package_list = ckan.getPackageList()
                
        db = Database('')
        return db.loadDbase('csvResourceIdList')
    
    def updateCSVResourceList(self):
        output = []
        package_list = ckan.getPackageList()
        
        for package in package_list:
            entity = self.getEntity(package)
            for resource in entity['resources']:
                if(self.isCSV(resource)):
                    output.append(resource['id'])
        
        db = Database('')
        db.saveDbase('csvResourceIdList', output)
        
    def createDefaultPageForAllCSV(self):
        from wikitoolsinterface import WikiToolsInterface
        wt = WikiToolsInterface()
        csvResources = self.getCSVResourceList()
        for position, resourceId in enumerate(csvResources):
            try:
                text = wt.generateDefaultPageForResource(resourceId)
                print wt.createPage(resourceId, text)
            except BaseException as e:
                print "Exception occured! " + str(e) 
            try:
                open(self.errorlogfile, "a+").write(resourceId.encode('utf-8') + ',')
                open(self.logfile, "a+").write('Element number from csvResource array: ' + str(position) + ' page created!\n')
            except:
                print 'cant write log files'
        return "Created all pages!"

#
# Auxilary interfaces
#

class LoggingInterface():
    pass

class PrintingInterface():
    def __str__(self):
        #print self.__class__
        output = {}
        for attr, value in self.__dict__.iteritems():
            output[attr] = value
        return str(output)

class ConfigurationInterface():
    ckan_base_url = ckanconfig.ckan_base_url
    api_url = ckanconfig.api_url #no trailing slash
    timeout = 10 #timeout for requesting info from CKAN API
    server_base_url = csv2rdfconfig.server_base_url
    
#
# CKAN interface - Actual API for the other pieces (server itself)
#

class Resource(PrintingInterface, ConfigurationInterface):
    """ Reflects the CKAN resource.
        Properties:
            resource_group_id, cache_last_updated, revision_timestamp, 
            api, webstore_last_updates, id, size, state, hash, description, 
            format, tracking_summary, mimetype_inner, mimetype, cache_url,
            name, created, url, webstore_url, last_modified, 
            position, revision_id, resource_type, package_name
            
            description - actual description of the resource
            format - can be csv, CSV, csv/text etc.
            tracking_summary: {u'total': 0, u'recent': 0}
            url - the download link
            position - position in the package if there are several resources
            package_name - necessary to initialize Package class
            ckan_base_url - http://publicdata.eu
            api_url - http://publicdata.eu/api
    """
    
    def __init__(self, resource_id):
        #Resource specific config params
        self.resource_dir = ckanconfig.resource_dir
        self.wiki_namespace = wikiconfig.wiki_namespace
        #CSV related
        self.csv_header_threshold = csv2rdfconfig.csv_header_threshold
        #Sparqlify related
        self.sparqlify_mappings_path = sparqlifyconfig.sparqlify_mappings_path
        self.rdf_files_path = sparqlifyconfig.rdf_files_path
        #Wiki init
        #TODO: exception: wikipedia not accessible
        self.site = wikitools.Wiki(wikiconfig.api_url)
        self.site.login(wikiconfig.username, password=wikiconfig.password)
        self.text = ''
        self.wiki_base_url = wikiconfig.wiki_base_url
        #Resource init
        self.id = resource_id
        self.initialize()
        self.package_name = self.request_package_name()
        self.filename = self.extract_filename_url()
    
    def initialize(self):
        data = json.dumps({'id': self.id})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = self.api_url + '/action/resource_show'
        r = requests.post(url, timeout=self.timeout, data=data, headers=headers)
        resource = json.loads(r.content)
        resource = resource["result"]
        for key in resource:
            setattr(self, key, resource[key])
    
    def request_package_name(self):
        url = self.api_url + '/rest/revision/' + self.revision_id
        r = requests.get(url, timeout=self.timeout)
        revision = json.loads(r.content)
        return revision["packages"][0]
        
    def extract_filename_url(self):
        return self.url.split('/')[-1].split('#')[0].split('?')[0]

    def _download(self):
        try:
            r = requests.get(self.url, timeout=self.timeout)
            file = Database(self.resource_dir)
            file.saveDbaseRaw(self.filename, r.content)
        except BaseException as e:
            print "Could not download the resource! " + str(e)
    
    def read_resource_file(self):
        try:
            file = Database(self.resource_dir)
            return file.loadDbaseRaw(self.filename)
        except IOError as e:
            # [Errno 2] No such file or directory
            if(e.errno == 2):
                self._download()
                self.read_resource_file()
        except BaseException as e:
            print "Could not read the resource! " + str(e)
            
    def _extract_csv_header_and_position(self):
        csv = None
        while(csv == None):
            csv = self.read_resource_file()
        
        # csv library implementation?    
        csv = csv.split('\n')
        for position, line in enumerate(csv):
            items = line.split(',')                
            overall = len(items)
            empty = 0
            for item in items:
                if(item == ''):
                    empty = empty + 1
            if(float(empty) / float(overall) < self.csv_header_threshold):
                return (position + 1, line)

    #
    # Wiki related methods (csv functions)
    #
    def create_wiki_page(self, captchaid=None, captchaword=None):
        """ Replace the whole resource page with the self.text
            DO NOT USE IN THE DEPLOYMENT MODE!!!
        """
        title = self.wiki_namespace + self.id
        page = wikitools.Page(self.site, title=title)
        
        try:
            if captchaid and captchaword:
                result = page.edit(text=text, bot=True, captchaid=captchaid, captchaword=captchaword)
            else:
                result = page.edit(text=text, bot=True)
        except BaseException as e:
            print 'Could not create a page on the publicdata.eu wiki! ' + str(e)
        
        if ('edit' in result) and ('result' in result['edit']) and (result['edit']['result'] == 'Success'):
            return result
        elif 'captcha' in result['edit']:
            captchaid = result['edit']['captcha']['id']
            captchaword = result['edit']['captcha']['question']
            captchaword = '-'.join(captchaword.split(u'\u2212'))
            captchaword = str(eval(captchaword))
            self.createPage(captchaid=captchaid, captchaword=captchaword)
        elif ('edit' in result) and ('result' in result['edit']) and (result['edit']['result'] != 'Success'):
            time.sleep(0.1)
            self.createPage(resourceId, text)
            
    def generate_default_wiki_page(self):
        package = Package(self.package_name)
        
        page = '{{CSV2RDFHeader}} \n'
        page += '\n'
        
        #link to the publicdata.eu dataset
        page += '{{CSV2RDFResourceLink | \n'
        page += 'packageId = '+package.name+' | \n'
        page += 'packageName = "'+package.title+'" | \n'
        page += 'resourceId = '+self.id+' | \n'
        page += 'resourceName = "'+self.description+'" | \n'
        page += '}} \n'
        page += '\n'
        
        #get the header from the csv file
        
        (headerPosition, header) = self._extract_csv_header_and_position()
        
        #CSV2RDF Template
        page += '{{RelCSV2RDF|\n'
        page += 'name = default-tranformation-configuration |\n'
        page += 'header = '+str(headerPosition)+' |\n'
        page += 'omitRows = -1 |\n'
        page += 'omitCols = -1 |\n'
        
        #Split header and create column definition
        i = 1
        for item in header.split(','):
            item = unidecode(item)
            page += 'col'+str(i)+' = '+item.rstrip()+' |\n'
            i = i + 1
        
        #Close template
        page += '}}\n'
        page += '\n'
                
        return page
    
    def request_wiki_page(self):
        title = self.wiki_namespace + self.id
        params = {'action':'query', 'prop':'revisions', 'rvprop':'content', 'titles':title}
        request = wikitools.APIRequest(self.site, params)
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
        
    def _extract_csv_configurations(self):        
        wiki_page = self.request_wiki_page()
        lines = wiki_page.split('\n')
        configs = []
        inside_config = False
        for line in lines:
            if(re.match('^{{RelCSV2RDF', line)):
                inside_config = True
                config = {}
                config['type'] = line[2:] #'RelCSV2RDF|'
                config['type'] = config['type'][:-1] # 'RelCSV2RDF'
                continue
            
            if(inside_config and re.match('^}}', line)):
                #push config to the configs
                configs.append(config)
                del config
                inside_config = False
                continue
            
            if(inside_config):
                prop = line.split('=')[0]
                value = str(line.split('=')[1])
                prop = prop.strip()
                value = ''.join(value[:-1].split())
                #value = urllib2.quote(value.encode("utf8"))
                config[prop] = value        
        return configs
    
    def _convert_csv_config_to_sparqlifyml(self, config):
        csv2rdfconfig = ''
        prefixcc = PrefixCC()
        #scan all colX values and extract prefixes
        prefixes = []
        properties = {} #properties['col1'] = id >>>> ?obs myprefix:id ?col1
        for key in config.keys():
            if(re.match('^col', key)):
                prefixes += prefixcc.extract_prefixes(config[key])
                properties[key] = config[key]
        #remove duplicates from prefixes
        prefixes = dict.fromkeys(prefixes).keys()
        #inject qb prefix
        prefixes += ['qb']
        for prefix in prefixes:
            csv2rdfconfig += prefixcc.get_sparqlify_namespace(prefix) + "\n"
        #Add custom prefix to non-prefixed values
        csv2rdfconfig += "Prefix publicdata:<http://wiki.publicdata.eu/ontology/>" + "\n"
        #Add fn sparqlify prefix
        csv2rdfconfig += "Prefix fn:<http://aksw.org/sparqlify/>" + "\n"
        
        csv2rdfconfig += "Create View Template DefaultView As" + "\n"
        csv2rdfconfig += "  CONSTRUCT {" + "\n"
        csv2rdfconfig += "      ?obs a qb:Observation ." + "\n"
        
        for prop in properties:
            csv2rdfconfig += "      ?obs "+ self._extract_property(properties[prop]) +" ?"+ prop + " .\n"
        csv2rdfconfig += "  }" + "\n"
        csv2rdfconfig += "  With" + "\n"
        #TODO: Check Claus e-mail and fix it!!! fn:rowId()
        csv2rdfconfig += "      ?obs = uri(concat('http://data.publicdata.eu/"+self.id+"#', ?rowId))" + "\n"
        for prop in properties:
            csv2rdfconfig += "      ?" + prop + " = " + self._extract_type(properties[prop], prop) + "\n"
        
        return csv2rdfconfig
    
    def _extract_property(self, prop):
        prop = prop.split('->')[0]
        if(len(prop.split(':')) == 1):
            return "publicdata:"+prop
        else:
            return prop
    
    def _extract_type(self, wikiString, column):
        column_number = column[3:]
        try:
            t = wikiString.split('->')[1]
            t = t.split('^^')[0]
            return "typedLiteral(?"+column_number+", "+t+")"
        except:
            return "plainLiteral(?"+column_number+")"
    
    def save_csv_configurations(self):
        db = Database(self.sparqlify_mappings_path)
        configs = self._extract_csv_configurations()
        for config in configs:
            sparqlifyml = self._convert_csv_config_to_sparqlifyml(config)
            filename = self.id + '_' + config['name'] + '.sparqlify'
            db.saveDbaseRaw(filename, sparqlifyml)
            
    #
    # Interface methods - getters
    #
    def get_id(self):
        return self.id
    
    def get_ckan_url(self):
        return str(self.ckan_base_url) + '/dataset/' + str(self.package_name) + '/resource/' + str(self.id)
    
    def get_csv_file_path(self):
        return os.path.realpath(self.resource_dir + self.filename)
    
    def get_csv_file_url(self):
        return str(self.server_base_url) + str(self.resource_dir) + str(self.filename)
        
    def get_sparqlify_configuration_path(self, configuration_name):
        if(os.path.exists(self.sparqlify_mappings_path + self.id + '_' + configuration_name + '.sparqlify')):
            return self.sparqlify_mappings_path + self.id + '_' + configuration_name + '.sparqlify'
        else:
            self.save_csv_configurations()
            return self.sparqlify_mappings_path + self.id + '_' + configuration_name + '.sparqlify'
    
    def get_sparqlify_configuration_url(self):
        pass
    
    def get_wiki_url(self):
        return self.wiki_base_url + '/wiki/' + self.wiki_namespace + self.id
        
class Package(PrintingInterface, ConfigurationInterface):
    """ Reflects the CKAN package.
        CKAN package contains one or several CKAN resources
        Properties:
            maintainer, package_name, maintainer_email, 
            id, metadata_created, ckan, relationships,
            metadata_modified, author, author_email, 
            download_url, state, version, license_id, type,
            resources: [], tags: [], tracking_summary, name,
            isopen, license, notes_rendered, url, ckan_url,
            notes, license_title, ratings_average,
            extras: {geographic_coverage, temporal_coverage-from,
            temporal_granularity, date_updated, published_via,
            mandate, precision, geographic_granularity,
            published_by, taxonomy_url, update_frequency,
            temporal_coverage-to, date_update_future, date_released},
            license_url, ratings_count, title, revision_id
            
            ckan - <ckanclient.CkanClient object at 0x972ac8c>
    """
    def __init__(self, package_name):
        self.name = package_name
        self.ckan = CkanClient(base_location=ckanconfig.api_url,
                               api_key=ckanconfig.api_key)
        self.initialize()
        
    def initialize(self):
        entity = self.ckan.package_entity_get(self.name)
        for key in entity:
            setattr(self, key, entity[key])
        
    def get_ckan_url(self):
        return str(self.ckan_base_url) + '/dataset/' + str(self.name)
# 
# For execution time measure:
# import time
# start_time = time.time()
# function()
# print time.time() - start_time, "seconds"
# 
            
if __name__ == '__main__':
    #Test area				
    #getting package list
    #ckan = CkanInterface(base_location='http://publicdata.eu/api', api_key='e7a928be-a3e8-4a34-b25e-ef641045bbaf')
    #package_list = ckan.getPackageList()
    #print ckan.getEntity("staff-organograms-and-pay-joint-nature-conservation-committee")
    #package_id
    
    resource = Resource('6023100d-1c76-4bee-9429-105caa061b9f')
    #print resource.get_ckan_url()
    #print resource.filename
    #print resource.get_csv_file_path()
    #print resource.get_csv_file_url()
    #print resource.get_wiki_url()
    #print resource.generate_default_wiki_page()
    #configs = resource.extract_csv_configurations()
    #print resource._convert_csv_config_to_sparqlifyml(configs[1])
    #print resource.get_sparqlify_configuration_path('default-tranformation-configuration')
    package = Package(resource.package_name)
    print package.name
    
    #print ckan.createDefaultPageForAllCSV()
    
    #create a list of csv resources (?)
    #ckan.updateCSVResourceList()
    #csvResources = ckan.getCSVResourceList()
    #print len(csvResources)
    #CSV: 12224
    #Overall: 55846
    