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
    
    def pFormat(self, object):
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        return pp.pformat(object)
    
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