import requests

class PrefixCC:
    def __init__(self):
        pass
    
    def getNamespace(self, prefix):
        r_string = 'http://prefix.cc/' + prefix + '.file.ini'
        r = requests.get(r_string)
        return r.text
    
    def getSparqlifyNamespace(self, prefix):
        ns = self.getNamespace(prefix)
        ns = ns.split('=')
        ns = "Prefix " + ns[0].strip() + ':' + '<' + ns[1].strip() + '>'
        return ns
    
    def extractPrefixes(self, string):
        #format here: foaf:birthday->xsd:date
        prefixes = []
        string = string.split('->')
        for substr in string:
            substr = substr.split(':')
            print len(substr)
            if(len(substr) > 1):
                prefixes.append(substr[0])
        return prefixes
    
if __name__ == '__main__':
    prefixcc = PrefixCC()
    print prefixcc.getSparqlifyNamespace('rdfs')