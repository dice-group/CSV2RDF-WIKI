import csv2rdf.nlp.nerd
import csv2rdf.config.config
text = """
Leipzig is a city in the federal state of Saxony, Germany. It has around 520,000 inhabitants[2] and is the heart of the Central German Metropolitan Region. Leipzig is situated about 150 kilometres (93 miles) south of Berlin at the confluence of the White Elster, Pleisse, and Parthe rivers at the southerly end of the North German Plain.
Leipzig has been a trade city at least since the time of the Holy Roman Empire,[3] sitting at the intersection of the Via Regia and Via Imperii, two important Medieval trade routes. At one time, Leipzig was one of the major European centres of learning and culture in fields such as music and publishing.[4] After World War II, Leipzig became a major urban centre within the German Democratic Republic (East Germany) but its cultural and economic importance declined,[4] despite East Germany being the richest economy in the Soviet Bloc.[5]
"""
timeout = 5
n = csv2rdf.nlp.nerd.NERD ('nerd.eurecom.fr', csv2rdf.config.config.nerd_api_key)
response = n.extract(text, 'combined', timeout)

print response
