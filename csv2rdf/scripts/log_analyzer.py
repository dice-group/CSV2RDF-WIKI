import csv2rdf.database
import csv2rdf.config.config
import re

db_log = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.main_log_folder)
main_log = db_log.loadDbaseRaw(csv2rdf.config.config.main_log_file)

def grep(string, list):
    expr = re.compile(string)
    for text in list:
        match = expr.search(text)
        if(match is not None):
            print match.string

grep(".*root.*DEBUG", main_log.split("\n"))
