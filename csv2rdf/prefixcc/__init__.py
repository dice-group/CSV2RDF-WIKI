import requests
from bs4 import BeautifulSoup

class PrefixCC:
    def __init__(self):
        pass

    def reverse_lookup(self, uri):
        r_string = 'http://prefix.cc/reverse?uri='+uri+'&format=ini'
        r = requests.get(r_string)
        bs = BeautifulSoup(r.text)
        return bs.find("div").text.strip()
    
    def get_namespace(self, prefix):
        r_string = 'http://prefix.cc/' + prefix + '.file.ini'
        r = requests.get(r_string)
        return r.text
    
    def get_sparqlify_namespace(self, prefix):
        ns = self.get_namespace(prefix)
        ns = ns.split('=')
        ns = "Prefix " + ns[0].strip() + ':' + '<' + ns[1].strip() + '>'
        return ns
    
    def extract_prefixes(self, string):
        #format here: foaf:birthday->xsd:date
        if(string.startswith('http')):
            return ''
        prefixes = []
        string = string.split('%5E%5E') # ^^
        for substr in string:
            substr = substr.split('%3A') # %3A = :
            if(len(substr) > 1):
                prefixes.append(substr[0])
        return prefixes
    
if __name__ == '__main__':
    prefixcc = PrefixCC()
    #print prefixcc.getSparqlifyNamespace('rdfs')
    print prefixcc.reverse_lookup("http://dbpedia.org/ontology/Organisation")
