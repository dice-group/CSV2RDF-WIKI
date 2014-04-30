from csv2rdf.ckan.resource import Resource

resource = Resource('')
f = open('iswc-datasets.csv')
for line in f:
    resource_uri = line.split(',')[1].strip()
    res = resource.search_by_uri(resource_uri)
    print res['id']

f.close()
