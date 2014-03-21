import requests
import json

class LovApi(object):
    SEARCH_API = "http://lov.okfn.org/dataset/lov/api/v1/search"

    def __init__(self):
        pass

    def atomize_query(self, query):
        atoms = query.split()
        return atoms

    def search(self, query):
        payload = {'q': query}
        r = requests.get(url=self.SEARCH_API, params=payload)
        assert r.status_code == 200
        return json.loads(r.content)

    def get_first_search_result(self, query):
        atoms = self.atomize_query(query)
        results = []
        for atom in atoms:
            query_result = self.search(query)
            if(query_result['results'] is not None and
               query_result['results'] != []):
                first_result = query_result['results'][0]
                results.append(first_result)
        return results

if __name__ == "__main__":
    lov_api = LovApi()
    result = lov_api.search("Entity")

    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(result.keys())
    pp.pprint(result['results'][0])
