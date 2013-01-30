import ckaninterface
from database import Database

import re
import magic
import os
import subprocess
from unidecode import unidecode
#
# CKAN scripting
#

class CkanInterface:
    def __init__(self):
        self.log_folder = 'script_logs/'
        self.conversion_log_folder = self.log_folder + 'rdf_conversion/'
        self.all_resources_folder = 'files/.all_resources/'
    
    def pFormat(self, object):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(object)
        
    def is_file_xml(self, filename):
        f = open(filename, "rU")
        validation_string = ".*<?xml.*"
        file_excerpt = f.read(1024)
        xml = re.match(validation_string, file_excerpt)
        f.close()
        if(xml):
            return True
        
    def delete_xml(self):
        files = self.get_files()
        for resource in files:
            if(self.is_file_xml('files/'+resource)):
                os.remove('files/'+resource)
    
    def download_n_random_csv(self, n):
        db = Database(self.log_folder)
        random_csv_filename = "random_csv.txt"
        import random
        ckan = ckaninterface.CKAN_Application()
        csv_resource_list = ckan.get_csv_resource_list()
        csv_resource_list_max = len(csv_resource_list) - 1
        for i in range(n):
            rand = random.randint(0, csv_resource_list_max)
            db.addDbaseRaw(random_csv_filename, str(rand) + "\n")
            resource = ckaninterface.Resource(csv_resource_list[rand])
            try:
                resource._download()
            except:
                pass
    
    def download_all_csv_resources(self):
        """ Download csv resources
            if resource unaccessible (404 or 503) - add to the list
            post-processing
                - check mimetype of the file
                - if not csv - report
        """
        db = Database(self.log_folder)
        download_all_log = "download_all_log.txt"
        ckan = ckaninterface.CKAN_Application()
        csv_resource_list = ckan.get_csv_resource_list()
        csv_resource_list_max = len(csv_resource_list) - 1
        for i in range(csv_resource_list_max):
            resource = ckaninterface.Resource(csv_resource_list[i])
            db.addDbaseRaw(download_all_log, resource._download())
            
    def process_download_all_log(self):
        db_logs = Database(self.log_folder)
        
        download_all_log = db_logs.loadDbaseRaw('download_all_log.txt')
        download_all_log = download_all_log.split('\n')
        resources_success = []
        resources_check = []
        resources_fail = []
        for line in download_all_log:
            if( re.match("^Could not download", line) ):
                resources_fail.append(line)
                continue
            
            if(line == ''):
                continue
            
            resource_id = line.split()[1]
            status_code = int(line.split()[3])
            if(status_code == 200):
                resources_success.append({resource_id: status_code})
            else:
                resources_check.append({resource_id: status_code})
        
        print len(resources_success)
        print len(resources_check)
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(resources_check)
    
    def delete_bad_response(self):
        db_logs = Database(self.log_folder)
        
        download_all_log = db_logs.loadDbaseRaw('download_all_log.txt')
        download_all_log = download_all_log.split('\n')
        resources_success = []
        resources_check = []
        resources_fail = []
        for line in download_all_log:
            if( re.match("^Could not download", line) ):
                resources_fail.append(line)
                continue
            
            if(line == ''):
                continue
            
            resource_id = line.split()[1]
            status_code = int(line.split()[3])
            if(status_code == 200):
                resources_success.append(resource_id)
            else:
                resources_check.append(resource_id)
        
        for resource in resources_check:
            if(os.path.exists('files/'+resource)):
                os.remove('files/'+resource)
        print 'resources clean-up complete!'
        
    def check_good_response(self):
        db_logs = Database(self.log_folder)
        
        download_all_log = db_logs.loadDbaseRaw('download_all_log.txt')
        download_all_log = download_all_log.split('\n')
        resources_success = []
        resources_check = []
        resources_fail = []
        for line in download_all_log:
            if( re.match("^Could not download", line) ):
                resources_fail.append(line)
                continue
            
            if(line == ''):
                continue
            
            resource_id = line.split()[1]
            status_code = int(line.split()[3])
            if(status_code == 200):
                resources_success.append(resource_id)
            else:
                resources_check.append(resource_id)
        
        bad_resources = []        
        for resource in resources_success:
            max_size_bytes = 1048576
            statinfo = os.stat('files/'+resource)
            if(statinfo.st_size > max_size_bytes):
                print str(resource) + ' larger than 1Mb!'
                continue
            
            file = open('files/'+resource, 'rb')
            string = file.read()
            file.close()
            
            if(re.match('.*html.*', string, flags=re.I)):
                print str(resource) + ' html page!'
                bad_resources.append(resource)
            else:
                print str(resource) + ' ok!'
                
    def delete_html_pages(self):
        db_logs = Database(self.log_folder)
        html_pages = db_logs.loadDbaseRaw('html_pages.txt')
        html_pages = html_pages.split('\n')
        for resource in html_pages:
            if(os.path.exists('files/'+resource) and resource != ''):
                os.remove('files/'+resource)
        
        print "clean-up complete!"
        
        
    def get_failed_resources_ckan_urls(self):
        db_logs = Database(self.log_folder)
        resources_fail = db_logs.loadDbaseRaw('resources_fail.csv')
        resources_fail = resources_fail.split('\n')
        for line in resources_fail:
            resource_id = line.strip()
            resource = ckaninterface.Resource(resource_id)
            print resource_id + ' ' + resource.ckan_url
            
    def choose_n_random(self, n=10):
        db = Database('files/.analyzed/')
        analyzed_ids = db.loadDbaseRaw('100_analyze_ids')
        analyzed_ids = analyzed_ids.split('\n')
        all_ids=self.get_files()
        csv_resource_list_max = len(all_ids) - 1
        
        output = []
        import random
        for i in range(n):
            rand = random.randint(0, csv_resource_list_max)
            if(not all_ids[rand] in analyzed_ids):
                output.append(all_ids[rand])
        
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        print pp.pprint(output)
    
    def create_wiki_pages_for_all(self, start_from=0):
        all_ids = self.get_files()
        overall = len(all_ids)
        for num, resource_id in enumerate(all_ids):
            if(num < start_from):
                continue
            print "creating page for resource " + str(num) + " out of " + str(overall)
            print str(resource_id)
            if(resource_id == ".analyzed" or resource_id == '.all-resources' or resource_id =='.broken_retrieved'
               or resource_id == "files.tar.gz"):
                continue
            resource = ckaninterface.Resource(resource_id)
            wiki_page = resource.generate_default_wiki_page()
            print resource.create_wiki_page(wiki_page)
            
        
    def get_files(self):
        directory = 'files/'
        file_list = os.listdir(directory)
        return file_list
    
    def get_sparqlified(self):
        directory = 'sparqlified/'
        file_list = os.listdir(directory)
        return file_list
        
    def convert_all_to_rdf(self, start_from = 0):        
        conversion_log = Database(self.conversion_log_folder)
        process_log = Database(self.log_folder)
        process_log_filename = "rdf_conversion.log"
        all_ids = self.get_files()
        overall = len(all_ids)
        for num, resource_id in enumerate(all_ids):
            if(num < start_from):
                continue
            print "Converting resource to RDF " + str(num) + " out of " + str(overall)
            print str(resource_id)
            string = "Converting resource to RDF " + str(num) + " out of " + str(overall) + "\n"
            process_log.addDbaseRaw(process_log_filename, string)
            string = str(resource_id) + "\n"
            process_log.addDbaseRaw(process_log_filename, string)
            
            #Skip folders
            if(resource_id == ".analyzed" or resource_id == '.all-resources' or resource_id =='.broken_retrieved'
               or resource_id == "files.tar.gz"):
                continue
            
            #Init the resource
            resource = ckaninterface.Resource(resource_id)
            
            #create wiki-page for resource
            string = "creating wiki page for resource" + "\n"
            process_log.addDbaseRaw(process_log_filename, string)
            wiki_page = resource.generate_default_wiki_page()
            string = str(resource.create_wiki_page(wiki_page))
            process_log.addDbaseRaw(process_log_filename, string)
            
            #transform resource to RDF
            sparqlify_message, returncode = resource.transform_to_rdf('default-tranformation-configuration')
            conversion_log.addDbaseRaw(resource_id + '.log', sparqlify_message + "\n" + str(returncode))
            
            
    def sync_files_sparqlified(self):
        #read files/
        files = self.get_files()
        #read sparqlified
        sparqlified = self.get_sparqlified()
        for num, resource in enumerate(sparqlified):
            sparqlified[num] = sparqlified[num][:36]
            resource_id = resource[:36]
            if not resource_id in files:
                os.remove('sparqlified/'+resource)
                
    def change_hash_to_slash(self):
        identificator = "[a-zA-Z0-9_]{8}-[a-zA-Z0-9_]{4}-[a-zA-Z0-9_]{4}-[a-zA-Z0-9_]{4}-[a-zA-Z0-9_]{12}"
        expr = "(<.*"+identificator+")#(\d+>)"
        replacement = r"\g<1>/\g<2>"
        sparqlified = self.get_sparqlified()
        for resource in sparqlified:
            #read and replace # with /
            f = open('sparqlified/'+resource, 'rU')
            string = f.read()
            new_string = re.sub(expr, replacement, string)
            f.close()
            
            f = open('sparqlified/'+resource, 'wb')
            f.write(new_string)
            f.close()
    
    #
    # Insert this code in the Resource class
    #
    
            
    def file_type_detect(self):
        print("xls")
        #excel file
        #self.detect_type('c00f3909-87a2-4874-aca7-c036638e2ec9') #ok
        self.detect_type('b9a2e1a8-bb97-414b-b8f8-9f93b2a8e09f') #word
        self.detect_type('da9fdb34-e592-4753-9b75-b1fbe9740653') #excel ?
        #self.detect_type('658ec97f-2345-4944-a9f5-6c963ee7cdee') #ok
        #self.detect_type('cd48e8e1-0708-44c8-87de-5428b04e4c3a') #ok
        #xlsx
        print("\nxlsx")
        self.detect_type('6bf556fe-8ef9-457c-bfd5-b2acf5e69ce2')
        self.detect_type('ed9b97cb-2269-492c-8684-fb7c73c948f4')
        self.detect_type('8873e873-aea4-4d40-94e9-bfe62830d17d')
        self.detect_type('28281ff8-b212-434f-9466-24574219cd4b')
        
        print("\narchives")
        #archives
        self.detect_type('efcd20f0-fd93-4649-8403-2d59d256ed32')
        self.detect_type('6f5a23f9-6130-4497-bc03-c6dd910e4baa')
        self.detect_type('9aed34e0-b50b-4417-aa1f-aeb18808b075')
        self.detect_type('cd8c19a9-8e9d-476a-acb1-0864231084a8')
        
        print("\nUTF-16")
        #UTF-16
        """
        self.detect_type('6c50ec67-8d52-44d4-8f7d-b4872783b638', folder='files/')
        self.detect_type('4fe6e99e-1f4b-416a-aa41-e302a0a06180', folder='files/')
        self.detect_type('49e7ca7f-1ee2-497d-bf5e-d92169526f38', folder='files/')
        self.detect_type('47055b3f-26f7-4869-a1a5-2ec6bf3a3618', folder='files/')
        self.detect_type('bc86b8a8-d7f9-479b-a105-040098b66bfa', folder='files/')
        self.detect_type('06a13464-5ff0-42c2-9690-4fa2eaeae37f', folder='files/')
        self.detect_type('94b3db8b-7f76-45aa-8b62-37ae0f910694', folder='files/')
        self.detect_type('bc86b8a8-d7f9-479b-a105-040098b66bfa', folder='files/')
        self.detect_type('8f1ee810-13a0-44e4-b583-f6ccf03448df', folder='files/')
        self.detect_type('3019d37d-4f3d-42a2-81a5-7824c153397d', folder='files/')
        self.detect_type('47055b3f-26f7-4869-a1a5-2ec6bf3a3618', folder='files/')
        self.detect_type('6c50ec67-8d52-44d4-8f7d-b4872783b638', folder='files/')
        self.detect_type('7d236042-5ff9-4f00-8fa1-a87fcf2b8f53', folder='files/')
        self.detect_type('4fe6e99e-1f4b-416a-aa41-e302a0a06180', folder='files/')
        self.detect_type('49e7ca7f-1ee2-497d-bf5e-d92169526f38', folder='files/')
        self.detect_type('ecc754dc-f7c8-4ca3-9ff1-98c5a720ffee', folder='files/')
        self.detect_type('e4487d64-5882-48ec-81db-20a89883f811', folder='files/')
        self.detect_type('15547cb7-8dc2-4f9f-9e11-12f8401d93bc', folder='files/')
        self.detect_type('25d95a3b-071d-453f-a8b4-28df254fc3ac', folder='files/')
        self.detect_type('53e3c309-59b0-4d83-9e58-9ddd9b97c6b6', folder='files/')
        self.detect_type('cbfdb8ac-f381-45ad-bffb-3086fd4dd746', folder='files/')
        self.detect_type('80ec8965-c48b-48c0-875f-3050f33abfad', folder='files/')
        self.detect_type('9377c95f-ec6b-4a37-a8ad-66577191b940', folder='files/')
        self.detect_type('c201283d-adfd-414d-972a-67b941cee9e0', folder='files/')
        self.detect_type('8587d5e4-3917-4283-930b-6548afbbd28d', folder='files/')
        self.detect_type('a715bcc2-f13e-4096-9132-f3bdb2ec6178', folder='files/')
        self.detect_type('b2ef9159-2f75-4d88-9875-c2bcf406e6ee', folder='files/')
        self.detect_type('ec041042-1952-4726-bbe3-39f02553d8c1', folder='files/')
        self.detect_type('3019d37d-4f3d-42a2-81a5-7824c153397d', folder='files/')        
        """
        
        
        
        
        
        print("\nokay files")
        #ok files
        self.detect_type('7e7c446c-e688-458e-b1b4-18709f1453e2')
        self.detect_type('fa31135e-a11d-4f73-9c9d-330404731073')
        self.detect_type('f768466a-977a-4980-8541-9588c443bd4c')
        self.detect_type('756cd753-43ce-486b-aff4-f4610b4d3b3f')
        
    def detect_type(self, id, folder = 'files_processed/.all-resources/'):
        """ Destructive, be careful to use
        """
        filename = folder + id
        mgc_encoding = magic.Magic(mime=False, magic_file=None, mime_encoding=True)
        mgc_string = magic.Magic(mime=False, magic_file=None, mime_encoding=False)
        #print mgc_string.from_file(filename)
        encoding = mgc_encoding.from_file(filename)
        info = mgc_string.from_file(filename)
        if(encoding == "utf-16le"):
            self.process_utf16(filename)
        elif(re.match("^binary", encoding) or
             re.match("^application/.*", encoding)):
            self.process_based_on(info, filename)
        else:
            print "File is okay"
            
    def process_based_on(self, info, filename):
        """
            The order is significant here
        """
        if(re.match(".*archive.*", info)):
            self.process_archive(filename)
        elif(re.match(".*Composite Document File V2 Document.*Excel.*", info) or
           re.match(".*Microsoft Excel 2007+.*", info) or
           not re.match(".*Composite Document File V2 Document.*Word.*", info)):
            self.process_xls(filename)
        elif(re.match(".*Composite Document File V2 Document.*Word.*", info)):
            #Word document
            #delete file
            pass
            
    def process_xls(self, resource_id):
        print resource_id
        ssconvert_call = ["ssconvert", #from gnumeric package
                          "-T",
                          "Gnumeric_stf:stf_csv",
                          resource_id,
                          resource_id]
        pipe = subprocess.Popen(ssconvert_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        print pipe_message
    
    def process_archive(self, filename):
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
            #delete file
            pass
    
    def process_utf16(self, filename):
        #decode to ascii
        #big files? memoryError
        #do it line by line!
        #iconv --from-code UTF-16LE --to-code ASCII//TRANSLIT 4fe6e99e-1f4b-416a-aa41-e302a0a06180 --output test
        f_in = open(filename, 'rU')
        f_out = open(filename+"-converted", 'wb')
        
        for piece in self.read_in_chunks(f_in):
            converted_piece = piece.decode('utf-16-le', errors='ignore')
            converted_piece = converted_piece.encode('ascii', errors='ignore')
            f_out.write(converted_piece)
        
        f_in.close()
        f_out.close()
        
    def read_in_chunks(self, file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data
            
            
    def convert_again(self):
        file = open('convert-again.csv')
        data = file.read()
        data = data.split('\n')
        for num, line in enumerate(data):
            print num
            resource_id = line.split()[0]
            print resource_id
            resource = ckaninterface.Resource(resource_id)
            print resource.validate()
            wiki_text = resource.generate_default_wiki_page()
            print resource.create_wiki_page(wiki_text)
            return_code = resource.transform_to_rdf('default-tranformation-configuration')
            print return_code
        file.close()
    
    def count_resources(self):
        import pickle
        data_folder = 'data/'
        file_list = os.listdir(data_folder)
        counter = 0
        for num, file in enumerate(file_list):
            if(file == "package_list"):
                continue
            f = open(data_folder + file)
            object = pickle.load(f)
            f.close()
            for resource in object['resources']:
                counter = counter + 1
        
        print counter    
        
    def read_data_folder(self):
        import pickle
        #get data folder list
        data_folder = 'data/'
        file_list = os.listdir(data_folder)
        
        stats = {
            'maintainer': {},
            'isopen': {},
            'author': {},
            'version': {},
            'license_id': {},
            'type': {},
            'mimetype': {},
            'format': {},
            'resource_type': {},
            'tags': {},
            'groups': {},
            'license': {},
            'license_title': {},
            'geographic_coverage': {},
            'geographical_granularity': {},
            'temporal_coverage-from': {},
            'temporal_coverage-to': {},
            'temporal_granularity': {},
            'national_statistic': {},
            'precision': {},
            'series': {},
            'date_released': {},
            'categories': {}            
        }
        
        import pprint
        printer = pprint.PrettyPrinter(indent=4)
        db = Database('stats/')    
        
        stats = db.loadDbase('stats14061')
                
        for num, file in enumerate(file_list):
            print num
            if(num < 14061 or file == "package_list"):
                continue
            f = open(data_folder + file)
            object = pickle.load(f)
            f.close()
            self.add_to_stats(object['maintainer'], 'maintainer', stats)
            self.add_to_stats(object['isopen'], 'isopen', stats)
            self.add_to_stats(object['author'], 'author', stats)
            self.add_to_stats(object['version'], 'version', stats)
            self.add_to_stats(object['type'], 'type', stats)
            for resource in object['resources']:
                self.add_to_stats(resource['mimetype'], 'mimetype', stats)
                self.add_to_stats(resource['format'], 'format', stats)
                self.add_to_stats(resource['resource_type'], 'resource_type', stats)
            
            for tag in object['tags']:
                self.add_to_stats(tag, 'tags', stats)
            
            for group in object['groups']:
                self.add_to_stats(group, 'groups', stats)
                
            self.add_to_stats(object['license'], 'license', stats)
            self.add_to_stats(object['license_title'], 'license_title', stats)
            
            try:
                self.add_to_stats(object['extras']['geographic_coverage'], 'geographic_coverage', stats)
                self.add_to_stats(object['extras']['geographical_granularity'], 'geographical_granularity', stats)
                self.add_to_stats(object['extras']['temporal_coverage-from'], 'temporal_coverage-from', stats)
                self.add_to_stats(object['extras']['temporal_coverage-to'], 'temporal_coverage-to', stats)
                self.add_to_stats(object['extras']['temporal_granularity'], 'temporal_granularity', stats)
                self.add_to_stats(object['extras']['series'], 'series', stats)
                self.add_to_stats(object['extras']['precision'], 'precision', stats)
                self.add_to_stats(object['extras']['national_statistic'], 'national_statistic', stats)
                self.add_to_stats(object['extras']['date_released'], 'date_released', stats)
                self.add_to_stats(object['extras']['categories'], 'categories', stats)
            except BaseException as e:
                pass
                #print str(e)
            
            db.saveDbase('stats' + str(num), stats)    
            
        #output stats to file
        print 'script executed!'
    
    def get_tag_count(self):
        import pickle
        #get data folder list
        data_folder = 'data/'
        file_list = os.listdir(data_folder)
        
        tag_usage = 0
        for num, file in enumerate(file_list):
            if(file == "package_list"):
                continue
            f = open(data_folder + file)
            object = pickle.load(f)
            if(not object['tags']):
                print "no tags here!"
            else:
                tag_usage = tag_usage + 1
                
        print tag_usage
    
    def get_stats(self):
        import pprint
        printer = pprint.PrettyPrinter(indent=4)
        db = Database('stats/')
        stats = db.loadDbase('stats17028')
        
        #tag cloud
        """
        tag_cloud = []
        for tag in stats['tags']:
            if stats['tags'][tag] > 15: #5 is okay
                for i in range(int(stats['tags'][tag] / 15)):
                    tag_cloud.append(tag)
            
        import json
        db.saveDbaseRaw('tag_cloud', json.dumps(tag_cloud))
        """
        
        #tags overall
        tag_usage = 0
        tag_count = 0
        for tag in stats['tags']:
            tag_usage = tag_usage + stats['tags'][tag]
            tag_count = tag_count + 1
        
        print tag_usage
        print tag_count
        
        
        #format statistics
        """
        import re
        csv = 0
        xml = 0
        excel = 0
        html = 0
        rdf = 0
        txt = 0
        pdf = 0
        doc = 0
        image = 0
        geo = 0
        unverified = 0
        zip = 0
        all = 0
        for format in stats['format']:
            all = all + stats['format'][format]
            
            if(re.match(".*csv.*", format, re.I)):
                csv = csv + stats['format'][format]
            
            if(re.match(".*xml.*", format, re.I) and
               not re.match(".*spreadsheet.*", format, re.I)):
                xml = xml + stats['format'][format]
            
            if(re.match(".*excel.*", format, re.I) or
               re.match(".*xls.*", format, re.I) or #4052!!
               re.match(".*spreadsheet.*", format, re.I) or
               re.match(".*ODS.*", format, re.I) or
               re.match(".*tsv.*", format, re.I)):
                excel = excel + stats['format'][format]
            
            if(re.match(".*html.*", format, re.I) or
               re.match(".*asp.*", format, re.I)):
                if(not re.match(".*rdf.*", format, re.I)):
                    html = html + stats['format'][format]
            
            if(re.match(".*rdf.*", format, re.I) or
               re.match(".*text/turtle.*", format, re.I) or
               re.match(".*bz2:nt.*", format, re.I)):
                rdf = rdf + stats['format'][format]
                
            if(re.match(".*txt.*", format, re.I) or
               re.match(".*text/plain.*", format, re.I) or
               re.match(".*Texto.*", format, re.I)):
                txt = txt + stats['format'][format]
            
            if(re.match(".*pdf.*", format, re.I)):
                pdf = pdf + stats['format'][format]
            
            if(re.match(".*DOC.*", format, re.I)):
                doc = doc + stats['format'][format]
            
            #graphical formats
            if(re.match(".*DXF.*", format, re.I) or
               re.match(".*GIF.*", format, re.I) or
               re.match(".*Imagen.*", format, re.I) or
               re.match(".*image.*", format, re.I) or
               re.match(".*jpeg.*", format, re.I) or
               re.match(".*shp.*", format, re.I) or
               re.match(".*tif.*", format, re.I)):
                image = image + stats['format'][format]
            
            #geographical
            if(re.match(".*WFS.*", format, re.I) or
               re.match(".*WMS.*", format, re.I) or
               re.match(".*google-earth.*", format, re.I)  or
               re.match(".*gpx.*", format, re.I) or
               re.match(".*kmz.*", format, re.I)):
                geo = geo + stats['format'][format]
            
            if(re.match(".*Unverified.*", format, re.I)):
                unverified = unverified + stats['format'][format]
            
            if(re.match(".*zip.*", format, re.I)):
                zip = zip + stats['format'][format]
                
            if(stats['format'][format] > 10):
                pass
                #print format
        print "all: " + str(all)
        print "csv: " + str(csv)
        print "xml: " + str(xml)
        print "excel: " + str(excel)
        print "html: " +  str(html)
        print "rdf: " + str(rdf)
        print "txt: " + str(txt)
        print "pdf: " + str(pdf)
        print "doc: " + str(doc)
        print "image: " + str(image)
        print "geo: " + str(geo)
        print "zip: " + str(zip)
        print "unverified: " + str(unverified)
        """
                
        
        #printer.pprint(stats)
    
    def add_to_stats(self, new_value, key, stats):
        #scan through the stats
        not_new = False
        
        if new_value in stats[key]:
            not_new = True
        
        #for stat in stats[key]:
        #    if(stat == new_value):
        #        not_new = True
                
        if(not_new):
            stats[key][new_value] = stats[key][new_value] + 1
        else:
            stats[key][new_value] = 1
    
    def convert_blacklisted_files(self):
        f = open('black_list')
        black_list = f.read()
        f.close()
        
        validate_list = [
                #'b408c0ca-7ef8-45e0-8e06-8755b20112fd',
                #'f4344e88-ec3e-4495-b774-0f989d1bc5c3',
                #'c0659fb9-ef60-4b7e-91e8-ca1c87462df6', -deleted
                #'b9a2e1a8-bb97-414b-b8f8-9f93b2a8e09f',
                #'796dda60-c9f3-4bc7-93f3-9cf341aa7f9b'
                #'ae26db03-51a9-43ee-8903-f6fe0ffe2fd7' deleted
            ]
        
        for resource_id in validate_list:
            #TODO: check for the loop!
            #resource = ckaninterface.Resource(resource_id)
            #print resource.get_ckan_url()
            #print resource.validate()
            pass
        
        for resource_id in black_list.split():
            resource = ckaninterface.Resource(resource_id)
            
            #print resource.get_wiki_url()
            return_code = resource.transform_to_rdf('default-tranformation-configuration')
            print return_code
            break
        
    def create_wanted_pages(self):
        page_string = "{{Inward Links For Property | {{PAGENAME}}}}"
        #get the list of wanted pages
        
        qpoffset = 0
        wanted_pages = []
        wanted_pages_chunk = self.get_wanted_page_list(qpoffset=qpoffset)
        while('query-continue' in wanted_pages_chunk):
            print "reading chunk with qpoffset = " + str(qpoffset)
            qpoffset = wanted_pages_chunk['query-continue']['querypage']['qpoffset']
            wanted_pages = wanted_pages + wanted_pages_chunk['query']['querypage']['results']
            wanted_pages_chunk = self.get_wanted_page_list(qpoffset=qpoffset)
        
        wanted_pages = wanted_pages + wanted_pages_chunk['query']['querypage']['results']
        
        print "reading wanted pages complete!"
        
        import wikiconfig
        import wikitools
        site = wikitools.Wiki(wikiconfig.api_url)
        site.login(wikiconfig.username, password=wikiconfig.password)
        self.wiki_base_url = wikiconfig.wiki_base_url
        
        #get titles
        for wanted_page in wanted_pages:
            print "Creating a page " + str(wanted_page['title'])
            page = wikitools.Page(site, title=wanted_page['title'])
            result = page.edit(text=page_string, bot=True)
        
    def get_wanted_page_list(self, qpoffset=0, api_url = "http://wiki.publicdata.eu/api.php?"):
        import requests
        import json
        query = str(api_url) + "format=json&" + "action=query&" + "list=querypage&" + "qppage=Wantedpages&" + "qplimit=500&" + "qpoffset=" + str(qpoffset)
        r = requests.get(query, timeout=10)
        result = json.loads(r.content)
        return result
    
    
if __name__ == '__main__':
    ckan = CkanInterface()
    ckan.create_wanted_pages()
    #ckan.convert_blacklisted_files()
    #ckan.get_tag_count()
    #ckan.count_resources()
    #ckan.get_stats()
    #print ckan._get_black_list()
    #ckan.convert_again()
    #ckan.file_type_detect()
    #ckan.get_failed_resources_ckan_urls()
    #ckan.check_good_response()
    #ckan.delete_html_pages()
    #ckan.choose_n_random(22)
    #8050
    #ckan.create_wiki_pages_for_all(start_from=9502)
    #try:
    #    ckan.convert_all_to_rdf(start_from=9061)
    #except BaseException as e:
    #    print str(e)
    
    #ckan.sync_files_sparqlified()
    #ckan.change_hash_to_slash()
    
    #ckan.download_n_random_csv(100)
    #resource = ckaninterface.Resource('c15e1fff-f9d8-41c7-9434-5d302a08be61')
    #print resource.ckan_url
    #resource._download()
    #
    #for i in range(1, 300, 1):
    #    string = """{{#if: {{{col"""+str(i)+"""|}}} | 
#{{!}} col"""+str(i)+""" {{!}}{{!}} [[has property::{{{col"""+str(i)+"""}}}]] 
#{{!}}- }}"""
#        print string
    
    #string = "prijmeni/pov.obec;0;3100;3201;3202;3203;3204;3205;3206;3207;3208;3211;3212;3225;3226;3230;3235;3240;3245;3250;3251;3255;3260;3261;3265;3266;3270;3275;3276;3301;3302;3303;3304;3305;3306;3307;3308;3325;3326;3330;3335;3336;3340;3341;3345;3350;3355;3356;3360;3401;3402;3403;3404;3408;3409;3410;3425;3430;3431;3435;3440;3441;3445;3450;3451;3452;3453;3455;3456;3465;3470;3501;3502;3503;3504;3505;3506;3507;3508;3509;3510;3525;3530;3531;3535;3540;3541;3545;3550;3551;3555;3556;3560;3565;3601;3602;3603;3604;3605;3606;3607;3608;3609;3610;3611;3625;3626;3630;3635;3640;3641;3645;3646;3647;3650;3651;3655;3656;3660;3661;3665;3666;3667;3670;3671;3675;3676;3677;3678;3679;3701;3704;3705;3706;3707;3708;3709;3710;3711;3712;3713;3714;3725;3730;3735;3736;3737;3738;3739;3740;3741;3742;3745;3746;3747;3748;3750;3751;3755;3760;3761;3765;3770;3771;3775;3780;3781;3785;3790;3791;3792;3801;3802;3803;3804;3805;3806;3808;3809;3810;3811;3825;3826;3830;3831;3832;3835;3836;3837;3838;3840;3841;3842;3843;3845;3846;3847;3850;3851;3852;3855;3860;3861;3865;3866;3870;3871;3901;;SUMA"
    #for num, item in enumerate(string.split(";")):
    #    print "col" + str(num + 1) + " = " + str(item) + " |"
    #    pass