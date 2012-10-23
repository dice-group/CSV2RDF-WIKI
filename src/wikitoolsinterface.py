from wikitools import wiki
from wikitools import api
import wikiconfig

class WikiToolsInterface:
    def __init__(self, api_url="http://wiki.publicdata.eu/api.php"):
        #init wikitools
        self.site = wiki.Wiki(api_url)
        #login with the data from wikiconfig.py
        self.site.login(wikiconfig.username, password=wikiconfig.password)
        self.site.setMaxlag = -1 #will wait forever
        
    def getPageContent(self, title):
        params = {'action':'query', 'prop':'revisions', 'rvprop':'content', 'titles':title}
        request = api.APIRequest(self.site, params)
        result = request.query()
        pages = result['query']['pages']
        for pageid in pages:
            page = pages[pageid]
            #get the last revision
            return page['revisions'][0]["*"]

if __name__ == '__main__':
    wt = WikiToolsInterface()
    print wt.getPageContent('Data:abstraction-licences-in-force-and-new-licences-determined')