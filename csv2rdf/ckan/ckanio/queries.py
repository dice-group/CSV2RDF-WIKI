import logging

import csv2rdf.config

import csv2rdf.ckan.ckanio
import csv2rdf.tabular.tabularfile

class Queries():
    def __init__(self):
        self.io = csv2rdf.ckan.ckanio.CkanIO()

    def get_outdated_and_new_csv_resources(self):
        """
            Compares the downloaded csv resources with 
            resources available in the CKAN (dump)
            and returns a list of outdated, new items
        """
        logging.info("Comparing the local csv resources with CKAN dump ... Started.")
        csv_ckan_list = self.io.get_csv_resource_list()

        #Making the list of ids
        csv_ckan_list_ids = []
        for resource in csv_ckan_list:
            csv_ckan_list_ids.append(resource['id'])

        tf = csv2rdf.tabular.tabularfile.TabularFile('')
        csv_local_list = tf.get_csv_resource_list_local()

        resources_outdated = []
        resources_new = []

        for resource in csv_local_list:
            if(not resource in csv_ckan_list_ids):
                resources_outdated.append(resource)

        for resource in csv_ckan_list_ids:
            if(not resource in csv_local_list and
               not resource in resources_outdated):
                resources_new.append(resource)

        logging.info("Comparing the local csv resources with CKAN dump ... Complete.")
        return (resources_outdated, resources_new)

    def get_available_formats(self):
        """
            Return list of sorted file formats
            used in the CKAN instance
        """
        resource_list = self.io.get_full_resource_list()
        formats = []
        for resource in resource_list:
            if(not resource['format'] in formats):
                formats.append(resource['format'])
        return sorted(formats)

    def get_format_stats(self):
        stats = {}
        from csv2rdf.ckan.ckanio.clustered_formats_pdeu import ClusteredFormats
        clusteredFormats = ClusteredFormats()
        resource_list = self.io.get_full_resource_list()
        stats['total'] = len(resource_list)
        for format_ in dir(clusteredFormats):
            stats[format_] = 0
        for resource in resource_list:
            for format_ in dir(clusteredFormats):
                exec("current_formats = clusteredFormats."+format_)
                if(resource['format'] in current_formats):
                    stats[format_] += 1
                    break
        return stats

    def get_rdf_and_sparql_list(self):
        rdf = self.io.get_resource_list("rdf")
        rdf_compressed = self.io.get_resource_list("rdf_compressed")
        rdf_html = self.io.get_resource_list("rdf_html")
        endpoints = self.io.get_resource_list("endpoint")
        process_list = rdf + rdf_compressed + rdf_html

        #Jens request: download link to rdf file, sparql end-point (if exist)
        #rdf_id, package_id, sparql_id, rdf_link, sparql_link
        #output_item = {'rdf_id': '',       # id
                       #'package_name': '', # package_name
                       #'rdf_url': '',     # url
                       #'sparql_id': '',    # (optional) also id, but in the endpoints list
                       #'sparql_url': '' } # (optional) also url, but in the endpoints list
        # order of the fields in csv output file
        fieldnames = ('rdf_id', 'sparql_id', 'package_name', 'rdf_url', 'sparql_url')
        output = []

        for resource in process_list:
            output_item = {}
            output_item['rdf_id'] = resource.id
            output_item['package_id'] = resource.package_id
            output_item['rdf_url'] = (resource.url).encode('utf-8')
            for endpoint in endpoints:
                if(resource.package_name == endpoint.package_name):
                    output_item['sparql_id'] = endpoint.id
                    output_item['sparql_url'] = endpoint.url
            output.append(output_item)

        return output

        #db = DatabasePlainFiles(config.data_path)
        #db.saveListToCSV(config.data_rdf_and_sparql_csv, output, fieldnames) 

    def detect_format(self, format_string):
        nt_formats = ["application/x-ntriples", "nt", "gzip:ntriples", "n-triples", "ntriples", "nt:meta", "nt:transparency-international-corruption-perceptions-index", "rdf, nt", "text/ntriples", "compressed tarfile containing n-triples", "bz2:nt", "gz:nt"]
        nq_formats = ["application/x-nquads", "nquads", "gzip::nquads", "gz:nq"]
        ttl_formats = ["text/turtle", "rdf/turtle", "ttl", "turtle", "application/turtle", "example/turtle", "example/x-turtle", "meta/turtle", "meta/urtle", "rdf/turtle", "text/ttl", "text/turtle", "ttl:e1:csv", "7z:ttl", "gz:ttl", "gz:ttl:owl", "ttl.bzip2"]
        n3_formats = ["text/n3", "n3", "rdf/n3", "application/n3", "example/n3", "example/n3 ", "example/rdf+n3", "text/rdf+n3"]
        rdf_formats = ["application/rdf+xml", "rdf", "rdf/xml", "owl", "application/rdf xml", "application/rdf+xml ", "application/rdfs", "example/owl", "example/rdf", "example/rdf xml", "example/rdf+xml", "meta/rdf+schema", "meta/rdf+xml", "meta/rdf-schema", "meta/rdf-schema ", "rdf+xml", "rdf+xml ", "rdf, owl", "rdf (gzipped)", "gzip:rdf/xml", ]
        sparql_formats = [ 'RDF endpoint', 'RDF, SPARQL+XML', 'SPARQ/JSON', 'SPARQL', 'SPARQL/JSON', 'SPARQL/XML', 'api/linked-data', 'api/sparql', 'api/sparql ', 'api/dcat', 'rdf, sparql', 'html, rdf, dcif', 'rdf, csv, xml', 'RDF/XML, HTML, JSON', 'RDF, SPARQL+XML', 'sparql' ]

        if format_string in nt_formats:
            return "nt"
        elif format_string in nq_formats:
            return "nq"
        elif format_string in ttl_formats:
            return "ttl"
        elif format_string in n3_formats:
            return "n3"
        elif format_string in rdf_formats:
            return "rdf"
        elif format_string in sparql_formats:
            return "sparql"
        else:
            return ""

    def get_rdf_for_lodstats(self):
        rdf = self.io.get_resource_list("rdf")
        rdf_compressed = self.io.get_resource_list("rdf_compressed")
        endpoints = self.io.get_resource_list("endpoint")
        process_list = rdf + rdf_compressed + endpoints

        fieldnames = ('resource_id', 'package_name', 'uri', 'format')
        output = []
        package_ids = []
        import md5

        for resource in process_list:
            output_item = {}
            output_item['resource_id'] = resource.id
            if(not resource.package_id in package_ids):
                output_item['package_id'] = resource.package_id
                package_ids.append(resource.package_id)
            else:
                output_item['package_name'] = resource.package_name + "_" + str(md5.new(resource.url.encode('utf-8')).hexdigest())
            output_item['uri'] = (resource.url).encode('utf-8')
            #routine from the LODStats
            format_string = resource.format.lower()
            output_item['format'] = self.detect_format(format_string)
            output.append(output_item)
       
        return output
        #db = DatabasePlainFiles(config.data_path)
        #db.saveListToCSV(config.data_for_lodstats, output, fieldnames) 

if __name__ == "__main__":
    q = Queries()

    #available_formats = q.get_available_formats()
    stats = q.get_format_stats()
    import ipdb; ipdb.set_trace()
    #print q.get_rdf_and_sparql_list()
    #print q.get_rdf_for_lodstats()
    #(outdated, new) = q.get_outdated_and_new_csv_resources()
    #print outdated
    #print new
