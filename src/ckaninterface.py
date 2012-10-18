#
# Logic for fetching and processing CKAN data
#
import ckanclient

class CkanInterface:
    def __init__(self, base_location=None, api_key=None):
        from database import Database
        self.base_location = base_location
        self.api_key = api_key
        self.ckan = ckanclient.CkanClient(base_location=base_location,
                                          api_key=api_key)
        self.db = Database('data/')
    def getEntity(self, entityName):
        try:
            entity = self.db.loadDbase(entityName)
        except IOError as error:
            print "I/O error({0}): {1}".format(error.errno, error.strerror)
            print "Creating new entity"
            entity = self.ckan.package_entity_get(entityName)
            self.db.saveDbase(entityName, entity)
        return entity
        
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
            
if __name__ == '__main__':
    #Test area				
    #getting package list
    ckan = CkanInterface(base_location='http://publicdata.eu/api', api_key='e7a928be-a3e8-4a34-b25e-ef641045bbaf')
    package_list = ckan.getPackageList()
    #getting one instance
    entityName = package_list[0]
    entity = ckan.getEntity(entityName)
    print entity
    #get all entities
    getAllEntities = raw_input("Get All Entities?(y/n):")
    if(getAllEntities == 'y'):
        print('Getting all entities')
        for entityName in package_list:
            print('Getting now: '+entityName)
            entity = ckan.getEntity(entityName)
            break
    else:
        pass