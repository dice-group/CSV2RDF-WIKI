import requests

class LODStats(object):
    def __init__(self):
        self.table_id = None
        self.table_header = None

    def set_table_id(self, table_id):
        self.table_id = table_id

    def set_table_header(self, table_header):
        self.table_header = table_header

    def request_datasets_for_linking(self):
        datasets_for_linking = []
        for item in self.table_header:
            if(not item['uri'] == ''):
                request_url = "http://stats.lod2.eu/vocab/search/" + item['uri']
                r = requests.get(request_url)
                datasets_for_linking = datasets_for_linking + r.json
        seen = set()
        datasets_no_duplicates = []
        duplicates = []
        for dataset in datasets_for_linking:
            t = tuple(dataset.items())
            if t not in seen:
                seen.add(t)
                datasets_no_duplicates.append(dataset)
            else:
                duplicates.append(dataset)
        return datasets_no_duplicates

if __name__ == "__main__":
    lodstats = LODStats()
    lodstats.set_table_id("13fd759b-549c-44dd-83a2-684e7a0b0147")
    header = "[{u'uri': u'http://dbpedia.org/ontology/department', u'label': u'department'}, {u'uri': u'', u'label': u'Entity'}, {u'uri': u'http://purl.org/dc/elements/1.1/date', u'label': u'Date'}, {u'uri': u'', u'label': u'Expense Type'}, {u'uri': u'', u'label': u'Expense Area'}, {u'uri': u'', u'label': u'Supplier'}, {u'uri': u'', u'label': u'Transaction Number'}, {u'uri': u'http://reference.data.gov.uk/def/payment#netAmount', u'label': u'net amount'}, {u'uri': u'', u'label': u'Vat Registration Number'}, {u'uri': u'', u'label': u'Invoice Number'}]"
    header = eval(header)
    lodstats.set_table_header(header)
    print lodstats.request_datasets_for_linking()
