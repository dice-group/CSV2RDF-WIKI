import ckaninterface
from database import Database
#
# CKAN scripting
#

class CkanInterface:
    def __init__(self):
        self.log_folder = 'script_logs/'
        self.all_resources_folder = 'files/.all_resources/'
    
    def pFormat(self, object):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(object)
    
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
        import re
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
        import re
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
        
        import os
        
        for resource in resources_check:
            if(os.path.exists('files/'+resource)):
                os.remove('files/'+resource)
        print 'resources clean-up complete!'
        
    def check_good_response(self):
        import re
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
        
        import os
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
        import os
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
        all_ids=self.get_all_ids()
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
    
    def create_wiki_pages_for_all(self):
        all_ids = self.get_all_ids()
        print all_ids[:20]
        for resource_id in all_ids:
            resource = ckaninterface.Resource(resource_id)
            wiki_page = resource.generate_default_wiki_page()
            resource.create_wiki_page(wiki_page)
        
        
    def get_all_ids(self):
        import os
        return os.listdir('files/')
    
if __name__ == '__main__':
    ckan = CkanInterface()
    #ckan.get_failed_resources_ckan_urls()
    #ckan.check_good_response()
    #ckan.delete_html_pages()
    #ckan.choose_n_random(22)
    ckan.create_wiki_pages_for_all()
    
    #ckan.download_n_random_csv(100)
    #resource = ckaninterface.Resource('c15e1fff-f9d8-41c7-9434-5d302a08be61')
    #print resource.ckan_url
    #resource._download()