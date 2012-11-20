import pickle
import os

class Database:
    def __init__(self, path = './'):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    
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
        
    def addDbaseRaw(self, filename, string):
        if not os.path.exists(self.path + filename) :
            open(self.path + filename, 'w').close()
        file = open(self.path + filename, 'a+')
        file.write(string)
        file.close()
    
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
        try:
            file = open(csvpath, 'rb')
            output = self._readnlines(file, n)
            file.close()
        except BaseException as e:
            print 'File read error: ' + str(e)
            output = ''
        return output
    
    def _readnlines(self,file, n):
        lines = []
        for x in range(0, n):
            lines.append(file.readline())
        return lines
    
if __name__ == '__main__':
    #reimport all objects as strings
    pass