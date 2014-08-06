import pypyodbc
from csv2rdf.config.config import virtuosoDSN
from csv2rdf.tabular.sparqlify import Sparqlify

class VirtuosoLoader(object):
    def __init__(self):
        connection = pypyodbc.connect(virtuosoDSN)
        self.cursor = connection.cursor()

    def load(self, filepath, graphUri):
        command = "DB.DBA.TTLP_MT (file_to_string_output ('%s'), '', '%s')" % (filepath, graphUri, )
        return self.cursor.execute(command)

    def getPathById(self, resourceId):
        sparqlify = Sparqlify(resourceId)
        return sparqlify.get_rdf_file_path('csv2rdf-interface-generated')

if __name__ == "__main__":
    vl = VirtuosoLoader()
    resourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    resourcePath = vl.getPathById(resourceId)
    resourceGraphUri = "http://data.publicdata.eu/%s"%(resourceId,)
    command = vl.load(resourcePath, resourceGraphUri)
    import ipdb; ipdb.set_trace()
