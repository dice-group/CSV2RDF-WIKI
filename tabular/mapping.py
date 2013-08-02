import os
import re
import logging

import urllib
import wikitools
from unidecode import unidecode
import tempfile

from config import config
from database import DatabasePlainFiles
from ckan.package import Package
from prefixcc import PrefixCC
from ckan.resource import Resource
from tabular.tabularfile import TabularFile
from ckan.ckanio import CkanIO

class Mapping():
    def __init__(self, resource_id = None):
        self.resource_id = resource_id
        self.wiki_site = wikitools.Wiki(config.wiki_api_url)
        self.wiki_site.login(config.wiki_username, password=config.wiki_password)
    
    def init(self):
        self.wiki_page = self.request_wiki_page()
        self.metadata = self.extract_metadata_from_wiki_page(self.wiki_page)
        self.mappings = self.extract_mappings_from_wiki_page(self.wiki_page)
        self.wiki_page = self.remove_blank_lines_from_wiki_page(self.wiki_page)
        self.mappings = self.process_mappings(self.mappings)
        self.save_csv_mappings(self.mappings)

    def process_mappings(self, mappings):
        for mapping in mappings:
            mapping['omitRows'] = self.process_omitRows(mapping['omitRows']) if mapping['omitRows'] != '-1' else [-1]
            mapping['omitCols'] = self.process_omitCols(mapping['omitCols']) if mapping['omitCols'] != '-1' else [-1]
            mapping['delimiter'] = mapping['delimiter'] if ('delimiter' in mapping) else ','
        return mappings

    def update_csv2rdf_wiki_page_list(self):
        params = {
                  'action':'query', 
                  'list':'allpages', 
                  'apnamespace':'505' #505 - csv2rdf namespace
                 }
        request = wikitools.APIRequest(self.wiki_site, params)
        result = request.query()
        db = DatabasePlainFiles(config.data_path)
        db.saveDbase(config.data_all_csv2rdf_pages, result)

    def get_csv2rdf_wiki_page_list(self):
        db = DatabasePlainFiles(config.data_path)
        return db.loadDbase(config.data_all_csv2rdf_pages)

    def get_all_csv2rdf_page_ids(self):
        """
            Returns the list of all wiki page ids
        """
        page_list = self.get_csv2rdf_wiki_page_list()
        titles = []
        for page in page_list['query']['allpages']:
            titles.append( page['title'][8:].lower() )
        return titles

    def request_wiki_page(self, resource_id = None):
        """
            Get a wiki page
            From the Mapping Wiki
        """
        if(not resource_id):
            resource_id = self.resource_id
        
        title = config.wiki_csv2rdf_namespace + resource_id
        params = {'action':'query', 'prop':'revisions', 'rvprop':'content', 'titles':title}
        request = wikitools.APIRequest(self.wiki_site, params)
        result = request.query()
        pages = result['query']['pages']
        try:
            for pageid in pages:
                page = pages[pageid]
                #get the last revision
                return page['revisions'][0]["*"]
        except:
            return False
    
    def extract_metadata_from_wiki_page(self, wiki_page):
        (templates, template_start, template_end) = self.parse_template(wiki_page, 'CSV2RDFMetadata')
        self.delete_template_from_wiki_page(template_start, template_end)
        if(len(templates) != 0):
            return templates[0]
        else:
            return {}

    def extract_mappings_from_wiki_page(self, wiki_page):        
        (templates, template_start, template_end) = self.parse_template(wiki_page, 'RelCSV2RDF')
        #self.delete_template_from_wiki_page(template_start, template_end)
        return templates

    def parse_template(self, wiki_page, template_name):
        lines = wiki_page.split('\n')
        templates = []
        inside_template = False        
        template_start = []
        template_end = []
        for num, line in enumerate(lines):
            if(re.match('^{{'+template_name, line)):
                inside_template = True
                template_start.append(num)
                template = {}
                template['type'] = line[2:] #'RelCSV2RDF|'
                template['type'] = template['type'][:-1] # 'RelCSV2RDF'
                continue
            
            if(inside_template and re.match('^}}', line)):
                #push mapping to the mappings
                templates.append(template)
                del template
                inside_template = False
                template_end.append(num)
                continue
            
            if(inside_template):
                if(len(line.split('=')) < 2):
                    continue
                    #line = lines[num-1] + lines[num]
                prop = line.split('=')[0]
                value = str(line.split('=')[1])
                prop = prop.strip()
                #Encode value to URL
                value = value[:-1]
                value = value.strip()
                if not prop == 'delimiter':
                    value = urllib.quote(value)
                template[prop] = value

        return (templates, template_start, template_end)

    def delete_template_from_wiki_page(self, template_start, template_end):
        lines = self.wiki_page.split('\n')
        for i in range(0, len(template_start)):
            for j in range(template_start[i], template_end[i] + 1):
                lines[j] = ''

        self.wiki_page = '\n'.join(lines)
    
    def remove_blank_lines_from_wiki_page(self, wiki_page):
        lines = wiki_page.split('\n')
        output = []
        for num, line in enumerate(lines):
            if(not line == ''):
                output.append(line)
        return '\n'.join(output)

    def convert_mapping_to_sparqlifyml(self, mapping, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
        
        csv2rdf_mapping = ''
        prefixcc = PrefixCC()
        #scan all colX values and extract prefixes
        prefixes = []
        properties = {} #properties['col1'] = id >>>> ?obs myprefix:id ?col1
        for key in mapping.keys():
            if(re.match('^col', key)):
                prefixes += prefixcc.extract_prefixes(mapping[key])
                properties[key] = mapping[key]
        #delete omitCols from the properties array and rearrange it
        for key in properties.keys():
            if(int(key[3:]) in mapping['omitCols']):
                del properties[key]
        #remove duplicates from prefixes
        prefixes = dict.fromkeys(prefixes).keys()
        #inject qb prefix
        #prefixes += ['qb']
        for prefix in prefixes:
            csv2rdf_mapping += prefixcc.get_sparqlify_namespace(prefix) + "\n"
        #Add custom prefix to non-prefixed values
        csv2rdf_mapping += "Prefix publicdata:<http://wiki.publicdata.eu/ontology/>" + "\n"
        #Add fn sparqlify prefix
        csv2rdf_mapping += "Prefix fn:<http://aksw.org/sparqlify/>" + "\n"
        
        csv2rdf_mapping += "Create View Template DefaultView As" + "\n"
        csv2rdf_mapping += "  CONSTRUCT {" + "\n"
        #csv2rdfconfig += "      ?obs a qb:Observation ." + "\n"
        
        for prop in properties:
            csv2rdf_mapping += "      ?obs "+ self._extract_property(properties[prop]) +" ?"+ prop + " .\n"
        csv2rdf_mapping += "  }" + "\n"
        csv2rdf_mapping += "  With" + "\n"
        csv2rdf_mapping += "      ?obs = uri(concat('http://data.publicdata.eu/"+resource_id+"/', ?rowId))" + "\n"
        for prop in properties:
            csv2rdf_mapping += "      ?" + prop + " = " + self._extract_type(properties[prop], prop) + "\n"

        return csv2rdf_mapping
    
    def _extract_property(self, prop):
        """
            Auxilary method for tabular to spaqrlify-ml convertion
        """
        print prop
        prop = prop.split('%5E%5E')[0]
        
        if(len(prop.split('%3A')) == 1): # %3A = :
            return "<http://wiki.publicdata.eu/ontology/"+str(prop)+">"
        else:
            return "<" + ':'.join(prop.split('%3A')) + ">"
    
    def _extract_type(self, wikiString, column):
        """
            Auxilary method for tabular to spaqrlify-ml convertion
        """
        column_number = column[3:]
        try:
            t = wikiString.split('%5E%5E')[1]
            #t = t.split('^^')[0]
            t = ':'.join(t.split('%3A')) 
            return "typedLiteral(?"+column_number+", "+t+")"
        except:
            return "plainLiteral(?"+column_number+")"
        
    def save_csv_mappings(self, mappings, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
            
        db = DatabasePlainFiles(config.sparqlify_mappings_path)
        for mapping in mappings:
            sparqlifyml = self.convert_mapping_to_sparqlifyml(mapping, resource_id=resource_id)
            filename = resource_id + '_' + mapping['name'] + '.sparqlify'
            db.saveDbaseRaw(filename, sparqlifyml)
    
    def create_wiki_page(self, text, resource_id = None):
        """
            Replace the whole resource page with the text
            User should be acknowledged bot!
        """
        if(not resource_id):
            resource_id = self.resource_id
            
        text = text.encode('utf-8')
        title = config.wiki_csv2rdf_namespace + resource_id
        page = wikitools.Page(self.wiki_site, title=title)
        result = page.edit(text=text, bot=True)
        return result

    def delete_wiki_page(self, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id

        title = config.wiki_csv2rdf_namespace + resource_id
        try:
            page = wikitools.Page(self.wiki_site, title=title)
            result = page.delete()
            return result
        except BaseException as e:
            logging.info("An exception occured, while deleting wiki page %s" % str(e))
    
    def generate_default_wiki_page(self, resource_id = None):
        """
            Check this method! Does not work yet!!!
        """
        if(not resource_id):
            resource_id = self.resource_id
        
        resource = Resource(resource_id)
        resource.init()
        package = Package(resource.package_name)
        tabular_file = TabularFile(resource_id)
        
        page = '{{CSV2RDFHeader}} \n'
        page += '\n'
        
        #link to the publicdata.eu dataset
        page += '{{CSV2RDFResourceLink | \n'
        page += 'packageId = '+package.name+' | \n'
        page += 'packageName = "'+package.title+'" | \n'
        page += 'resourceId = '+resource.id+' | \n'
        page += 'resourceName = "'+resource.description+'" | \n'
        page += '}} \n'
        page += '\n'
        
        #get the header from the csv file
        
        header_position = tabular_file.get_header_position()
        header = tabular_file.extract_header(header_position)
        
        #CSV2RDF Template
        page += '{{RelCSV2RDF|\n'
        page += 'name = default-tranformation-configuration |\n'
        page += 'header = '+str(header_position)+' |\n'
        page += 'omitRows = -1 |\n'
        page += 'omitCols = -1 |\n'
        
        #Split header and create column definition
        for num, item in enumerate(header):
            item = unidecode(item)
            page += 'col'+str(num+1)+' = '+item.rstrip()+' |\n'
            if(num > 500): # too many columns in this csv OR bad format
                break
        
        #Close template
        page += '}}\n'
        page += '\n'
        
        page = page.encode('utf-8')
                
        return page

    def update_metadata(self):
        self.update_metadata_csv_filesize()
        self.update_metadata_csv_number_of_lines()
        self.update_metadata_csv_number_of_columns()
        self.update_metadata_rdf_number_of_triples()
        self.update_metadata_rdf_last_sparqlified()
        self.add_metadata_to_wiki_page()
        self.create_wiki_page(self.wiki_page)
        
    def update_metadata_csv_filesize(self):
        tabular_file = TabularFile(self.resource_id) 
        csv_filesize = tabular_file.get_csv_filesize()
        self.metadata['filesize'] = str(csv_filesize)

    def update_metadata_csv_number_of_lines(self):
        tabular_file = TabularFile(self.resource_id)
        csv_number_of_lines = tabular_file.get_csv_number_of_lines()
        self.metadata['csv_number_of_lines'] = str(csv_number_of_lines)

    def update_metadata_csv_number_of_columns(self):
        cols = 0
        for key in self.mappings[0].keys():
            if(re.match("^col.*", key)):
                cols += 1
        self.metadata['csv_number_of_columns'] = str(cols)

    def update_metadata_rdf_number_of_triples(self):
        """
            using the default mapping here (mapping 0)
        """
        rdf_filename = self.resource_id + "_" + self.mappings[0]['name'] + ".rdf"
        db = DatabasePlainFiles(config.rdf_files_path)
        rdf_number_of_triples = db.count_line_number(rdf_filename)
        self.metadata['rdf_number_of_triples'] = str(rdf_number_of_triples)

    def update_metadata_rdf_last_sparqlified(self):
        rdf_filename = self.resource_id + "_" + self.mappings[0]['name'] + ".rdf"
        db = DatabasePlainFiles(config.rdf_files_path)
        rdf_last_sparqlified = db.get_last_access_time(rdf_filename)
        self.metadata['rdf_last_sparqlified'] = str(rdf_last_sparqlified)

    def add_metadata_to_wiki_page(self):
        metadata = self.metadata
        lines = self.wiki_page.split('\n')
        lines.append("{{CSV2RDFMetadata|")
        for key in metadata.keys():
            lines.append(key +"="+metadata[key]+" |")
        lines.append("}}")
        self.wiki_page = '\n'.join(lines)
        
    def process_omitRows(self, string):
        output = []
        ranges = string.split('%2C')
        for r in ranges:
            if(len(r.split('-')) < 2):
                output.append(int(r))
            else:
                start = int(r.split('-')[0])
                end = int(r.split('-')[1])
                list = range(start, end + 1)
                output = output + list
        return output

    def process_omitCols(self, string):
        return self.process_omitRows(string)

    def process_file(self, original_file_path, mapping_current):
        omitRows = mapping_current['omitRows']

        try:
            processed_file = tempfile.NamedTemporaryFile(delete=False)
            original_file = open(original_file_path, 'rU')
            for line_num, line in enumerate(original_file.readlines()):
                #line_num = 0 is a header, we do not process it
                if(not line_num in omitRows):
                    processed_file.write(line)
        except BaseException as e:
            print str(e)
        finally:
            original_file.close()
            processed_file.close()

        return processed_file

    def get_mapping_path(self, configuration_name, resource_id=None):
        if(not resource_id):
            resource_id = self.resource_id
        file_path = os.path.join(config.sparqlify_mappings_path, str(resource_id) + '_' + str(configuration_name) + '.sparqlify')
        if(os.path.exists(file_path)):
            return file_path
        else:
            return False
    
    def get_mapping_url(self, configuration_name, resource_id = None):
        if(not resource_id):
            resource_id = self.resource_id
        file_path = self.get_mapping_path(configuration_name, resource_id=resource_id)
        if(file_path):
            return os.path.join(config.server_base_url, self.get_mapping_path(configuration_name, resource_id=resource_id))
        else:
            return False
        
    def get_mapping_names(self):
        names = []
        for mapping in self.mappings:
            names.append(mapping['name'])
        return names
    
    def get_mapping_by_name(self, mapping_name):
        for mapping in self.mappings:
            if(mapping['name'] == mapping_name):
                return mapping
        #Nothing was found
        return False

    def get_outdated_and_new_wiki_pages(self):
        logging.info("Looking for outdated and new wiki pages ... Started.")
        tf = TabularFile('')
        resources_ids = tf.get_csv_resource_list_local()

        page_ids_list = self.get_all_csv2rdf_page_ids()
        pages_outdated = []
        pages_new = [] 

        for page_id in page_ids_list:
            if(not page_id in resources_ids):
                pages_outdated.append(page_id) 

        for resource_id in resources_ids:
            if(not resource_id in page_ids_list):
                pages_new.append(resource_id)

        logging.info("Looking for outdated and new wiki pages ... Complete.")
        return (pages_outdated, pages_new)
    
if __name__ == '__main__':
    #mapping = Mapping('1aa9c015-3c65-4385-8d34-60ca0a875728')
    mapping = Mapping('00e0737c-6920-479a-9916-ff83b9de692c')
    mapping.init()
    mapping.update_metadata()
    #print mapping.wiki_page
    #print mapping.metadata
    #print mapping.mappings
    #print mapping.update_csv2rdf_wiki_page_list()
    #print mapping.get_mapping_names()
    #wiki_page = mapping.request_wiki_page('1aa9c015-3c65-4385-8d34-60ca0a875728')
    #mappings = mapping.extract_mappings_from_wiki_page(wiki_page)
    #sparqlified_mapping = mapping.convert_mapping_to_sparqlifyml(mappings[0], resource_id='1aa9c015-3c65-4385-8d34-60ca0a875728')
    #mapping.save_csv_mappings(mappings, resource_id='1aa9c015-3c65-4385-8d34-60ca0a875728')
    #mapping.create_wiki_page('Testing the test page!', resource_id='1aa9c015-3c65-4385-8d34-60ca0a875728')
    #print mapping.generate_default_wiki_page(resource_id='1aa9c015-3c65-4385-8d34-60ca0a875728')
    #print mapping.get_mapping_path('ijfosij', resource_id='1aa9c015-3c65-4385-8d34-60ca0a875728')
    #print mapping.get_mapping_url('ijfosij', resource_id='1aa9c015-3c65-4385-8d34-60ca0a875728')
