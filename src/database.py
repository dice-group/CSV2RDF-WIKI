import pickle

class Database:
    def __init__(self, path):
        self.path = path
    
    def saveDbase(self, filename, object):
        "save object to file"
        file = open(self.path + filename, 'wb')
        pickle.dump(object, file, protocol=pickle.HIGHEST_PROTOCOL)
        file.close()
    
    def loadDbase(self, filename):
        "load object from file"
        file = open(self.path + filename, 'rb')
        object = pickle.load(file)
        file.close()
        return object
    
    def saveDbaseRaw(self, filename, string):
        "save string to file"
        file = open(self.path + filename, 'wb')
        file.write(string)
        file.close()
        
    def loadDbaseRaw(self, filename):
        "load string from file"
        file = open(self.path + filename, 'rb')
        return file.read()
    
    #
    # CKAN specific functions
    #
    
    def loadResourceCSV(self, resourceId, n=5):
        #get the resource filename (from url)
        from ckaninterface import CkanInterface
        ckan = CkanInterface()
        resource = ckan.getResourceById(resourceId)
        filename = ckan.extractFilenameFromUrl(resource['url'])
        entityName = ckan.getResourcePackage(resourceId)
        csvpath = 'files/'+entityName+'/' + filename

        file = open(csvpath, 'rb')
        output = self._readnlines(file, n)
        file.close()
        return output
        #try:
        #    with open(csvpath, 'r') as csvfile:
        #        head=[csvfile.next() for x in xrange(n)]
        #    return head
        #except BaseException as e:
        #    return e
    
    def _readnlines(self,file, n):
        lines = []
        for x in range(0, n):
            lines.append(file.readline())
        return lines
    
if __name__ == '__main__':
    #reimport all objects as strings
    
    pass