import RDF
from csv2rdf.ckan.resource import Resource
from csv2rdf.ckan.package import Package

resource_id = "69f7e7ad-1efa-4f0c-8f0b-71949f55a743"

if __name__ == "__main__":
    res = Resource(resource_id)
    res.init()
    package_name = res.request_package_name()
    package = Package(package_name)
    package_metadata = package.get_metadata()
    model = RDF.Model()
    parser = RDF.Parser()
    parser.parse_string_into_model(model, package_metadata, "http://localhost/")
    
    #title is label
    title_predicate = "http://purl.org/dc/terms/title"
    qs = RDF.Statement(subject = None, 
                       predicate = RDF.Node(uri_string = title_predicate), 
                       object = None)
    for statement in model.find_statements(qs): 
        title_statement = statement
        break
    #description is comment
    description_predicate = "http://purl.org/dc/terms/description"
    qs = RDF.Statement(subject = None, 
                       predicate = RDF.Node(uri_string = description_predicate), 
                       object = None)
    for statement in model.find_statements(qs): 
        description_statement = statement
        break

    output_model = RDF.Model()
    output_model.add_statement(title_statement)
    output_model.add_statement(description_statement)

    serializer = RDF.Serializer()
    serialized_output = serializer.serialize_model_to_string(output_model)
