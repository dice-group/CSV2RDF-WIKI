from ckanclient import CkanClient
import wikitools
from database import Database
import os
from unidecode import unidecode
import re
import urllib2
from prefixcc import PrefixCC
import subprocess
import json
import requests
requests.defaults.danger_mode = True
import time
import csv
import urllib
import magic

#Configs
import ckanconfig
import csv2rdfconfig
import wikiconfig
import sparqlifyconfig

#
# Auxilary interfaces
#

class LoggingInterface():
    
    log_file = "log.log"
    error_file = "error.log"
    
    def log(self, string):
        db = Database()
        db.addDbaseRaw(log_file, string)
    
    def error(self, string):
        db = Database()
        db.addDbaseRaw(error_file, string)

class AuxilaryInterface():
    def __str__(self):
        #print self.__class__
        output = {}
        for attr, value in self.__dict__.iteritems():
            output[attr] = value
        return str(output)
    
    def extract_filename_url(self, url):
        return url.split('/')[-1].split('#')[0].split('?')[0]

class ConfigurationInterface():
    sparqlify_jar = sparqlifyconfig.sparqlify_jar
    ckan_base_url = ckanconfig.ckan_base_url
    api_url = ckanconfig.api_url #no trailing slash
    timeout = 25 #timeout for requesting info from CKAN API
    server_base_url = csv2rdfconfig.server_base_url
    resource_dir = ckanconfig.resource_dir
    
    #Sparqlify related
    rdf_files_exposed_path = sparqlifyconfig.rdf_files_exposed_path
    rdf_files_path = sparqlifyconfig.rdf_files_path
    sparqlify_mappings_path = sparqlifyconfig.sparqlify_mappings_path
    
#
# CKAN interface - Actual API for the other pieces (server itself)
#

class Resource(AuxilaryInterface, ConfigurationInterface):
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
        self.wiki_namespace = wikiconfig.wiki_namespace
        #CSV related
        self.csv_header_threshold = csv2rdfconfig.csv_header_threshold
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
        #self.filename = self.extract_filename_url(self.url)
        self.filename = self.id
        self.ckan_url = self.get_ckan_url()
        self.wiki_url = self.get_wiki_url()
    
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

    def _download(self):
        try:
            r = requests.get(self.url, timeout=self.timeout)
            file = Database(self.resource_dir)
            file.saveDbaseRaw(self.filename, r.content)
            return "resource " + str(self.id) + " status_code " + str(r.status_code) + "\n"
        except BaseException as e:
            return "Could not download the resource "+str(self.id)+" ! "+str(e)+"\n"
    
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
            
    def _extract_csv_header_and_position_first_line(self):
        """
            This function take the first line of the csv file
            as a header. Should work in 60% of all cases.
        """
        with open(self.resource_dir + self.filename, 'rU') as csvfile:
            #dialect does not work good!
            #dialect = csv.Sniffer().sniff(csvfile.read(1024))
            #csvfile.seek(0)
            reader = csv.reader(csvfile)
            try:
                for row in reader:
                    return row
            except BaseException as e:
                print str(e)
                return []
            #print csv.Sniffer().has_header(csvfile.read(1024))
            #csvfile.seek(0)
            
        
    #
    # Wiki related methods (csv functions)
    #
    def create_wiki_page(self, text, captchaid=None, captchaword=None):
        """ Replace the whole resource page with the text
            DO NOT USE IN THE PRODUCTION!!!
        """
        title = self.wiki_namespace + self.id
        page = wikitools.Page(self.site, title=title)
        result = ''
        try:
            if captchaid and captchaword:
                result = page.edit(text=text, bot=True, captchaid=captchaid, captchaword=captchaword)
            else:
                result = page.edit(text=text, bot=True)
        except BaseException as e:
            print 'Could not create a page on the publicdata.eu wiki! ' + str(e)
        
        if ('edit' in result) and ('result' in result['edit']) and (result['edit']['result'] == 'Success'):
            return result
        elif ('edit' in result) and ('captcha' in result['edit']):
            captchaid = result['edit']['captcha']['id']
            captchaword = result['edit']['captcha']['question']
            captchaword = '-'.join(captchaword.split(u'\u2212'))
            captchaword = str(eval(captchaword))
            time.sleep(0.1)
            self.create_wiki_page(text=text, captchaid=captchaid, captchaword=captchaword)
        elif ('edit' in result) and ('result' in result['edit']) and (result['edit']['result'] != 'Success'):
            time.sleep(0.1)
            self.create_wiki_page(text=text, captchaid=captchaid, captchaword=captchaword)
            
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
        
        headerPosition = 1
        header = self._extract_csv_header_and_position_first_line()
        
        #CSV2RDF Template
        page += '{{RelCSV2RDF|\n'
        page += 'name = default-tranformation-configuration |\n'
        page += 'header = '+str(headerPosition)+' |\n'
        page += 'omitRows = -1 |\n'
        page += 'omitCols = -1 |\n'
        
        #Split header and create column definition
        i = 1
        for item in header:
            item = unidecode(item)
            page += 'col'+str(i)+' = '+item.rstrip()+' |\n'
            i = i + 1
        
        #Close template
        page += '}}\n'
        page += '\n'
        
        page = page.encode('utf-8')
                
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
        for num, line in enumerate(lines):
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
                if(len(line.split('=')) < 2):
                    continue
                    #line = lines[num-1] + lines[num]
                prop = line.split('=')[0]
                value = str(line.split('=')[1])
                prop = prop.strip()
                #Encode value to URL
                value = value[:-1]
                value = value.strip()
                value = urllib.quote(value)
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
        #prefixes += ['qb']
        for prefix in prefixes:
            csv2rdfconfig += prefixcc.get_sparqlify_namespace(prefix) + "\n"
        #Add custom prefix to non-prefixed values
        csv2rdfconfig += "Prefix publicdata:<http://wiki.publicdata.eu/ontology/>" + "\n"
        #Add fn sparqlify prefix
        csv2rdfconfig += "Prefix fn:<http://aksw.org/sparqlify/>" + "\n"
        
        csv2rdfconfig += "Create View Template DefaultView As" + "\n"
        csv2rdfconfig += "  CONSTRUCT {" + "\n"
        #csv2rdfconfig += "      ?obs a qb:Observation ." + "\n"
        
        for prop in properties:
            csv2rdfconfig += "      ?obs "+ self._extract_property(properties[prop]) +" ?"+ prop + " .\n"
        csv2rdfconfig += "  }" + "\n"
        csv2rdfconfig += "  With" + "\n"
        csv2rdfconfig += "      ?obs = uri(concat('http://data.publicdata.eu/"+self.id+"/', ?rowId))" + "\n"
        for prop in properties:
            csv2rdfconfig += "      ?" + prop + " = " + self._extract_type(properties[prop], prop) + "\n"
        
        return csv2rdfconfig
    
    def _extract_property(self, prop):
        prop = prop.split('->')[0]
        if(len(prop.split(':')) == 1):
            return "<http://wiki.publicdata.eu/ontology/"+str(prop)+">"
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
    # Sparqlify
    #
    
    def transform_to_rdf(self, configuration_name):
        sparqlify_call = ["java",
                          "-cp", self.sparqlify_jar,
                          "org.aksw.sparqlify.csv.CsvMapperCliMain",
                          "-f", self.get_csv_file_path(),
                          "-c", self.get_sparqlify_configuration_path(configuration_name)]        
        rdf_filename = self.rdf_files_path + self.id + '_' + configuration_name + '.rdf'
        f = open(rdf_filename, 'w')
        pipe = subprocess.Popen(sparqlify_call, stdout=f, stderr=subprocess.PIPE)
        sparqlify_message = pipe.stderr.read()
        pipe.stderr.close()
        f.close()
        
        return sparqlify_message, pipe.returncode
    
    #
    # Validation methods here
    #
    
    def validate(self):
        """ Destructive, be careful to use
        """
        filename = self.resource_dir + self.filename
        mgc_encoding = magic.Magic(mime=False, magic_file=None, mime_encoding=True)
        mgc_string = magic.Magic(mime=False, magic_file=None, mime_encoding=False)
        encoding = mgc_encoding.from_file(filename)
        info = mgc_string.from_file(filename)
        if(encoding == "utf-16le"):
            self._process_utf16(filename)
        elif(re.match("^binary", encoding) or
             re.match("^application/.*", encoding)):
            self._process_based_on(info, filename)
        else:
            return True
            
    def _process_based_on(self, info, filename):
        """
            The order is significant here
        """
        if(re.match(".*archive.*", info)):
            self._process_archive(filename)
        elif(re.match(".*Composite Document File V2 Document.*Excel.*", info) or
           re.match(".*Microsoft Excel 2007+.*", info) or
           not re.match(".*Composite Document File V2 Document.*Word.*", info)):
            self._process_xls(filename)
        elif(re.match(".*Composite Document File V2 Document.*Word.*", info)):
            #Word document
            self._delete(filename)
            return False
            
    def _process_xls(self, resource_id):
        print resource_id
        ssconvert_call = ["ssconvert", #from gnumeric package
                          "-T",
                          "Gnumeric_stf:stf_csv",
                          resource_id,
                          resource_id]
        pipe = subprocess.Popen(ssconvert_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        self.validate()
    
    def _process_archive(self, filename):
        #unzip archive
        #check number of files
        sevenza_call = ["7za", 
                          "l",
                          filename]
        pipe = subprocess.Popen(sevenza_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        pattern = "(\d+) files"
        number_of_files = re.search(pattern, pipe_message)
        number_of_files = int(number_of_files.group(0).split()[0])
        if(number_of_files < 2):
            #get the file name
            pattern = "\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+.{5}\s+\d+\s+\d+\s+(.*)\n"
            original_filename = re.search(pattern, pipe_message)
            original_filename = original_filename.group(0).split()[-1]
            #extract
            sevenza_call = ["7za", 
                            "e",
                            filename]
            pipe = subprocess.Popen(sevenza_call, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            #move to original
            mv_call = ["mv",
                       original_filename,
                       filename]
            pipe = subprocess.Popen(mv_call, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
        else:
            #more than 1 file in the archive
            self._delete(filename)
            return False
    
    def _process_utf16(self, filename):
        f_in = open(filename, 'rU')
        f_out = open(filename+"-converted", 'wb')
        
        for piece in self._read_in_chunks(f_in):
            converted_piece = piece.decode('utf-16-le', errors='ignore')
            converted_piece = converted_piece.encode('ascii', errors='ignore')
            f_out.write(converted_piece)
        
        f_in.close()
        f_out.close()
        
        #move converted to original
        mv_call = ["mv",
                    filename+"-converted",
                    filename]
        pipe = subprocess.Popen(mv_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        
    def _read_in_chunks(self, file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data
            
    def _delete(self, filename):
        rm_call = ["rm",
                    filename]
        pipe = subprocess.Popen(rm_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
            
    #
    # Interface methods - getters
    # Use these methods to get all the necessary info!
    #
    
    def get_id(self):
        return self.id
    
    def get_ckan_url(self):
        return str(self.ckan_base_url) + '/dataset/' + str(self.package_name) + '/resource/' + str(self.id)
    
    def get_csv_file_path(self):
        if(os.path.exists(self.resource_dir + self.filename)):
            return self.resource_dir + self.filename
        else:
            self._download()
            return self.resource_dir + self.filename
    
    def get_csv_file_url(self):
        return str(self.server_base_url) + str(self.resource_dir) + str(self.filename)
        
    def get_sparqlify_configuration_path(self, configuration_name):
        self.save_csv_configurations()
        return self.sparqlify_mappings_path + self.id + '_' + configuration_name + '.sparqlify'
    
    def get_sparqlify_configuration_url(self, configuration_name):
        return self.server_base_url + self.get_sparqlify_configuration_path(configuration_name)
    
    def get_wiki_url(self):
        return self.wiki_base_url + '/wiki/' + self.wiki_namespace + self.id
    
    def get_rdf_file_path(self, configuration_name):
        if(os.path.exists(self.rdf_files_path + self.id + '_' + configuration_name + '.rdf')):
            return self.rdf_files_path + self.id + '_' + configuration_name + '.rdf'
        else:
            self.transform_to_rdf(configuration_name)
            return self.rdf_files_path + self.id + '_' + configuration_name + '.rdf'
        
    def get_rdf_file_url(self, configuration_name):
        return self.server_base_url + self.get_rdf_file_path(configuration_name)
        
class Package(AuxilaryInterface, ConfigurationInterface):
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
    
    def download_all_resources(self):
        db = Database(self.resource_dir)
        for resource in self.resources:
            url = resource['url']
            filename = self.extract_filename_url(url)
            try:
                r = requests.get(url, timeout=self.timeout)
                db.saveDbaseRaw(filename, r.content)
            except BaseException as e:
                print "Could not get the resource " + str(resource['id']) + " ! " + str(e)
            
    def is_resource_csv(self, resource):
        if(re.search( r'csv', resource['format'], re.M|re.I)):
            return True
        else:
            return False
    
    #
    # Interface - getters
    #
        
    def get_ckan_url(self):
        return str(self.ckan_base_url) + '/dataset/' + str(self.name)
        
        
class CKAN_Application(AuxilaryInterface, ConfigurationInterface):
    """ Reflects the CKAN application itself,
        interfaces for getting packages etc.
    """
    def __init__(self):
        self.ckan = CkanClient(base_location=ckanconfig.api_url,
                               api_key=ckanconfig.api_key)
        self.csv_resource_list_filename = 'csv_resource_list'
        
    def update_csv_resource_list(self):
        output = []
        package_list = self.get_package_list()
        
        for package in package_list:
            entity = Package(package)
            for resource in entity['resources']:
                if(self.isCSV(resource)):
                    output.append(resource['id'])
        
        db = Database()
        db.saveDbase(self.csv_resource_list_filename, output)
        
    def get_package_list(self):
        return self.ckan.package_list()
        
    def get_csv_resource_list(self):
        db = Database()
        return db.loadDbase(self.csv_resource_list_filename)
        
    def get_sparqlified_list(self):
        return os.listdir(self.rdf_files_exposed_path)
        
    def update_sparqlified_list(self):
        #update list - make soft links to the files
        rdf_files = os.listdir(self.rdf_files_path)
        for rdf_file in rdf_files:
            #make a soft link
            link_to = os.path.abspath(self.rdf_files_path + rdf_file)
            resource_id = rdf_file[:36] #take resource_id part only
            link = self.rdf_files_exposed_path + resource_id
            make_soft_link = ["ln",
                              "-f",
                              "-s",
                              link_to,
                              link]
            pipe = subprocess.Popen(make_soft_link, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            print pipe_message
        
    
# 
# For execution time measure:
# import time
# start_time = time.time()
# function()
# print time.time() - start_time, "seconds"
# 
            
if __name__ == '__main__':
    ckan = CKAN_Application()
    ckan.get_sparqlified_list()
    #Test area				
    #getting package list
    #ckan = CkanInterface(base_location='http://publicdata.eu/api', api_key='e7a928be-a3e8-4a34-b25e-ef641045bbaf')
    #package_list = ckan.getPackageList()
    #print ckan.getEntity("staff-organograms-and-pay-joint-nature-conservation-committee")
    #package_id
    
    #wiki_text = resource.generate_default_wiki_page()
    #resource.create_wiki_page(wiki_text)
    #(sparqlify_message, return_code) = resource.transform_to_rdf('default-tranformation-configuration')
    #print sparqlify_message
    #print resource.get_ckan_url()
    
    #print resource.get_sparqlify_configuration_url('default-tranformation-configuration')
    #print resource.get_rdf_file_url('default-tranformation-configuration')
    #print resource.filename
    #print resource.get_csv_file_path()
    #print resource.get_csv_file_url()
    #print resource.get_wiki_url()
    #print resource.generate_default_wiki_page()
    #configs = resource.extract_csv_configurations()
    #print resource._convert_csv_config_to_sparqlifyml(configs[1])
    #print resource.get_sparqlify_configuration_path('default-tranformation-configuration')
    #package = Package(resource.package_name)
    #print package.resources
    #package.download_all_resources()
    
    #print ckan.createDefaultPageForAllCSV()
    
    #create a list of csv resources (?)
    #ckan.updateCSVResourceList()
    #csvResources = ckan.getCSVResourceList()
    #print len(csvResources)
    #CSV: 12224
    #Overall: 55846
    