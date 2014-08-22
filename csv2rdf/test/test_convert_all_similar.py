testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
from csv2rdf.tabular.mapping import Mapping
mappings = Mapping(testResourceId)
mappings.init_mappings_only()
mappingName = 'csv2rdf-interface-generated-with-datatype'
mapping = mappings.get_mapping_by_name(mappingName)
header = mappings.get_mapping_headers()[1]

import urllib
class_ = {'value': urllib.unquote(mapping['class']),
          'label': ''}
#emulating json object from csv2rdf-interface
headerJson = []
for item in header[mappingName]:
    headerItem = {'label': '',
                  'uri': item[1]}
    headerJson.append(headerItem)

from csv2rdf.semanticmediawiki.query import SMWQuery
smwquery = SMWQuery()
idList = smwquery.fetchAllResourceIdsFromDataset(testResourceId)
for id in idList:
    mapping = Mapping(id)
    mapping.update_mapping(headerJson, class_)
