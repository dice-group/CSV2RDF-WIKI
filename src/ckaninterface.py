#s
# Logic for fetching and processing CKAN data
#
import ckanclient
from database import Database
import os
import requests
requests.defaults.danger_mode = True

class CkanInterface:
    def __init__(self, base_location=None, api_key=None):
        self.base_location = base_location
        self.api_key = api_key
        self.ckan = ckanclient.CkanClient(base_location=base_location,
                                          api_key=api_key)
        self.db = Database('data/')
        self.errorlog = open('error.log', 'wb')
        self.log = open('log.log', 'wb')
    def getEntity(self, entityName):
        try:
            entity = self.db.loadDbase(entityName)
        except IOError as error:
            print "I/O error({0}): {1}".format(error.errno, error.strerror)
            print "Creating new entity"
            entity = self.ckan.package_entity_get(entityName)
            self.db.saveDbase(entityName, entity)
        return entity
    
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
                    r = requests.get(url, timeout=10)
                    self.filesdb.saveDbase(filename, r.content)
                    self.log.write(entityName.encode('utf-8') + ' ' + url.encode('utf-8') + ' OK!\n')
                    self.log.flush()
                except Exception as e:
                    self.errorlog.write(entityName.encode('utf-8') + ' ' + url.encode('utf-8') + ' ' + str(e) + '\n')
                    self.errorlog.flush()
        

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
    ckan = CkanInterface(base_location='http://publicdata.eu/api', api_key='e7a928be-a3e8-4a34-b25e-ef641045bbaf')
    package_list = ckan.getPackageList()
    #getting one instance
    entityName = package_list[0]
    entity = ckan.getEntity(entityName)
    #print ckan.pFormat(entity)
    #get all entities    
    getAllEntities = raw_input("Get All Entities?(y/n):")
    if(getAllEntities == 'y'):
        print('Getting all entities')
        for entityName in package_list:
            #83.9261538982 seconds from data/ files
            #print('Getting now: '+entityName)
            entity = ckan.getEntity(entityName)
            ckan.downloadEntityResources(entity)
    else:
        pass
    #working with ambulance-call-outs-to-animal-attack-incidents
    entityName = "ambulance-call-outs-to-animal-attack-incidents"
    ckan.getEntityFiles(entityName)
    