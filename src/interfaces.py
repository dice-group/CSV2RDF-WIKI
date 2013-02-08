class LoggingInterface():
    
    log_file = "log.log"
    error_file = "error.log"
    
    def log(self, string):
        db = Database()
        db.addDbaseRaw(log_file, string)
    
    def error(self, string):
        db = Database()
        db.addDbaseRaw(error_file, string)

class AuxilaryInterface():
    def __str__(self):
        #print self.__class__
        output = {}
        for attr, value in self.__dict__.iteritems():
            output[attr] = value
        return str(output)
    
    def extract_filename_url(self, url):
        return url.split('/')[-1].split('#')[0].split('?')[0]    