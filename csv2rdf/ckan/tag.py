import requests
import json

import csv2rdf.interfaces
import csv2rdf.config.config

class Tag(csv2rdf.interfaces.AuxilaryInterface):
    def __init__(self, tag_name):
        self.name = tag_name
        #self.tag_list = self.get_tag_list()

    def get_tag_list(self):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = csv2rdf.config.config.ckan_api_url + '/action/tag_list'
        r = requests.post(url, timeout=csv2rdf.config.config.ckan_request_timeout, headers=headers)
        assert r.ok, r
        load = json.loads(r.content)
        tag_list = load['result']
        return tag_list

    def show_tag(self, tag_name):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = csv2rdf.config.config.ckan_api_url + '/action/tag_show?id='+str(tag_name)
        r = requests.post(url, timeout=csv2rdf.config.config.ckan_request_timeout, headers=headers)
        assert r.ok, r
        load = json.loads(r.content)
        tag_info = load['result']
        packages = tag_info['packages']
        #filter out empty packages:
        packages_not_empty = []
        for package in packages:
            if(package['num_resources'] > 0):
                packages_not_empty.append(package)
        return (tag_info, packages_not_empty)

    def get_tag_csv_resources(self, tag_name):
        resources = []
        import re
        match_csv = re.compile("csv", re.I|re.M)
        (tag_info, packages_not_empty) = self.show_tag(tag_name)
        for package in packages_not_empty:
            for resource in package['resources']:
                if("mime_type" in resource and match_csv.match(resource['mime_type'])):
                    resources.append(resource)
                elif("format" in resource and match_csv.match(resource['format'])):
                    resources.append(resource)
        return resources

    def interesting_tags(self):
        return [#'abfall',
                #'abfalle',
                'absence',
                'absent',
                'academic',
                'academic-staff',
                'aeroport',
                #'aeroporti',
                #'aeroporto',
                'aerodrome',
                #'bahnhof',
                #'biologica',
                #'biologico',
                'biologie',
                'charity',
                'child',
                'contracts',
                'crime',
                'crimes',
                'defence',
                'dental',
                'developer',
                'development',
                'drug',
                'eco',
                'ecological',
                'energy',
                'engine',
                'engines',
                'exams',
                'films',
                'finance',
                'finances',
                #'fleisch',
                'free',
                'free-wifi',
                'free-wi-fi',
                'game',
                'games',
                'gaming',
                'geologia',
                'geography',
                'health',
                #'klinik',
                'lake',
                'lakes',
                'museum',
                'museums',
                #'musei',
                #'museo',
                #'museos',
                'music',
                #'musik',
                #'musica',
                'nutrition',
                'nutritional',
                'nutricion',
                'park',
                'parks',
                'parks-and-gardens',
                'pension',
                'pensions',
                'phd',
                'phds',
                'police',
                'population',
                'professional',
                #'professionali',
                'professionals',
                'public-art',
                'public-health',
                'regulation',
                'regulations',
                'satellite',
                'school',
                'science',
                'sciences',
                #'statistica',
                'statistical',
                'survivor',
                'survivors',
                'tank',
                'tanks',
                'temperature',
                'temperatures',
                'tourist',
                'tourists',
                'transport',
                'transports',
                'vegetables',
                'waste',
                'wlan',
                'zoologie']

if __name__ == '__main__':
    tag = Tag('')
    import pprint
    pp = pprint.PrettyPrinter()
    tag_1 = tag.interesting_tags()[0]
    pp.pprint(tag.get_tag_csv_resources(tag_1))
    pass
