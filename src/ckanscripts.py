import ckaninterface
from database import Database
#
# CKAN scripting
#

class CkanInterface:
    def __init__(self):
        self.log_folder = 'script_logs/'
    
    def pFormat(self, object):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(object)
        
    def createDefaultPageForAllCSV(self):
        pass
    
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
    
    
if __name__ == '__main__':
    ckan = CkanInterface()
    ckan.download_all_csv_resources()
    #ckan.download_n_random_csv(100)
    #resource = ckaninterface.Resource('726120e3-1188-4473-9f77-27e011ab1438')
    #resource._download()