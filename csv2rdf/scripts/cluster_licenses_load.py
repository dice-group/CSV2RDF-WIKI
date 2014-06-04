import cPickle
from csv2rdf.config.config import data_path

def encode(string):
    if(string is None):
        return ""
    elif(type(string) is int):
        return string
    elif(string is ""):
        return "N/A"
    else:
        return string.encode('utf-8')

filename = "licenses_precise21March2014"
filepath = data_path + filename
licenses = cPickle.load(open(filepath, 'rb'))
for license in licenses:
    arr = [str(encode(license)), 
           str(encode(licenses[license]['count'])), 
           str(encode(licenses[license]['license_title'])), 
           str(encode(licenses[license]['license_url'])), 
           str(encode(licenses[license]['license']))]
    print ", ".join(arr)
