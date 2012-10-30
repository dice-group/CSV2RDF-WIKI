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
    
if __name__ == '__main__':
    #reimport all objects as strings
    
    pass