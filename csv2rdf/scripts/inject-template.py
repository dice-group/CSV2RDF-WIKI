import csv2rdf.tabular.mapping

#Get all ids files less than 1 MB
geo_qb_templates = "{{faceteCSV2RDF}}{{qbCSV2RDF}}"
f = open("lessthanonemb.list", 'r')
for line in f.readlines():
    print id
    id = line.split('/')[-1].rstrip()
    mapping = csv2rdf.tabular.mapping.Mapping(resource_id = id)
    mapping.wiki_page = mapping.request_wiki_page()
    if(not mapping.wiki_page):
        continue
    (templates, template_start, template_end) = mapping.parse_template(mapping.wiki_page, 'CSV2RDFResourceLink')
    mapping.wiki_page = mapping.wiki_page.split('\n')
    split_place = int(template_end[0]) + 1
    mapping.wiki_page = mapping.wiki_page[:split_place] + [geo_qb_templates] + mapping.wiki_page[split_place:]
    mapping.wiki_page = '\n'.join(mapping.wiki_page)
    mapping.create_wiki_page(mapping.wiki_page)
