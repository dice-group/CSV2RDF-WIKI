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
print idList
idList = eval("""['072a069f-cc21-483d-a9a8-c049aa9e8ba0', '693b6fc9-bce9-494c-9292-4e98bdcb6c10', '12ba5362-9e8d-460e-accb-0a03e33c2d24', 'cb18edb9-04bd-4df5-927a-9b121944cef1', 'af1dc053-0398-4a6d-8a06-06d22d8e07cf', '8f7bfae4-253f-4400-b787-b7c7c3427530', 'a27e5902-2081-4bdc-b600-c026b7283f1c', 'daacea8c-789a-4cfd-b685-c927e9adf54c', 'e8b8eb07-148f-492e-a2a1-95a663644ec5', 'e0a6ee5c-ea48-42b8-aab2-ab318a2d1a50', '02f31d80-40cc-496d-ad79-2cf02daa5675', '96d17099-5d94-405d-8954-8193c75b6551', 'de339077-8435-4a33-9219-24d10a62c0ef', '8d31c47b-535c-49f5-ae06-86f2ebc4ab2e', '909871d8-3e8b-4d0a-b83d-c29e403e20a9', '7eb16313-6cb8-4177-a942-dcdb78eba08d', 'b9fd3b25-20c1-4aa7-94ae-223b0cb47383', '905f5fb0-3f89-428a-801e-75f5003fbfc6', 'b2beaf4a-5229-4674-83fe-21f6b8b039a0', '141cd493-3237-428b-a56b-b88fd5f9da7c', '0a3dd35c-9c1b-42de-82c2-c2ddd6d0556f']""")
import logging
#id = idList[6]
#id = idList[18]
print len(idList)
id = idList[21]
#for id in idList:
mapping = Mapping(id)
mapping.update_mapping(headerJson, class_)
