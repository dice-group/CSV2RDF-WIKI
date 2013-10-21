import os
import re
import subprocess
import logging

import csv
import requests
from magic import Magic

import csv2rdf.config
import csv2rdf.database
import csv2rdf.ckan.resource
import csv2rdf.interfaces


class TabularFile(csv2rdf.interfaces.StringMatchInterface):
    def __init__(self, resource_id):
        self.id = resource_id
        self.filename = self.id

    def download(self):
        resource = csv2rdf.ckan.resource.Resource(self.id)
        resource.init()
        try:
            r = requests.get(resource.url, timeout=csv2rdf.config.config.ckan_request_timeout)
            assert r.ok, r
            file = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
            if(not file.is_exists(self.filename)):
                file.saveDbaseRaw(self.filename, r.content)
                logging.info("File %s downloaded and saved successfully" % self.id)
            else:
                logging.info("File %s already exists" % self.id)
        except BaseException as e:
            logging.warning("Could not download the resource %s " % str(self.id))
            logging.warning("Exception occured: %s" % str(e))
        finally:
            return self.get_csv_file_path()

    def get_csv_filesize(self):
        filepath = self.get_csv_file_path()
        return os.path.getsize(filepath)

    def get_csv_number_of_lines(self):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
        return db.count_line_number(self.filename)

    def delete(self):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
        db.delete(self.filename)
        return True

    def get_csv_file_path(self):
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
        if(db.is_exists(self.filename)):
            return db.get_path_to_file(self.filename)
        else:
            return False

    def get_csv_file_url(self):
        file_path = self.get_csv_file_path()
        if(file_path):
            return os.path.join(csv2rdf.config.config.server_base_url, file_path)
        else:
            return False

    def read_resource_file(self):
        try:
            file = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
            return file.loadDbaseRaw(self.filename)
        except BaseException as e:
            print "Could not read the resource! " + str(e)
            return False

    def get_header_position(self):
        """
            Stub for the header recognition problem!
        """
        return 1

    def extract_header(self, position):
        """
            This function take the first line of the csv file
            as a header. Should work in 60% of all cases.
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
        with open(db.get_path_to_file(self.filename), 'rU') as csvfile:
            reader = csv.reader(csvfile)
            try:
                for num, row in enumerate(reader, 1):
                    if(num == position):
                        return row
            except BaseException as e:
                print str(e)
                return []

    def validate(self):
        filename = self.filename
        (encoding, info) = self.get_info_about()
        logging.debug("File encoding: %s" % encoding)
        logging.debug("File info: %s" % info)

        #Delete matches
        if(self.match('.*mswordbinary.*', encoding)):
            logging.debug("Resource %s is a MS Word, deleting." % self.id)
            self.delete()
            return True

        if(self.match('.*Composite Document.*No summary.*', encoding)):
            logging.debug("Resource %s is unknown Composite Document, deleting." % self.id)
            self.delete()
            return True

        if(self.match('.*BitTorrent.*', info)):
            logging.debug("Resource %s is a BitTorrent file, deleting." % self.id)
            self.delete()
            return True

        if(self.match('.*PDF.*', info)):
            logging.debug("Resource %s is a PDF file, deleting." % self.id)
            self.delete()
            return True

        if(self.match('.*XML.*', info)):
            logging.debug("Resource %s is a XML document, deleting." % self.id)
            self.delete()
            return True

        if(self.match('.*HTML.*', info)):
            logging.debug("Resource %s is a HTML document, deleting." % self.id)
            self.delete()
            return True

        #MS Excel
        if(self.match('.*ms-excelbinary.*', encoding) or
           self.match('.*Excel.*', info)):
            logging.debug("Resource %s is a Excel table, processing." % self.id)
            self._process_xls(filename)
            return True

        #Archive data
        if(self.match('.*gzip.*', info) or
           self.match('.*tarbinary.*', encoding)):
            logging.debug("Resource %s is a .tar.gz archive, processing." % self.id)
            self._process_archive(filename)
            return True

        if(self.match('.*7-zip.*', info) or
           self.match('.*Zip.*', info)):
            logging.debug("Resource %s is a .7z or .zip archive, processing." % self.id)
            self._process_archive(filename)
            return True

        #UTF-8 UTF-16LE encodings
        if(self.match('.*utf-16le.*', encoding)):
            logging.debug("Resource %s has UTF-16LE encoding, processing." % self.id)
            self._process_utf16(filename)
            return True

        if(self.match('.*utf-8.*', encoding)):
            logging.debug("Resource %s has UTF-8 encoding, processing." % self.id)
            return True

        #no matches?
        return True

    def get_info_about(self):
        """
            return (encoding, info) tuple
            info is a plain string and has to be parsed
        """
        db = csv2rdf.database.DatabasePlainFiles(csv2rdf.config.config.resources_path)
        filename = db.get_path_to_file(self.filename)
        mgc_encoding = Magic(mime=False, mime_encoding=True)
        mgc_string = Magic(mime=False, mime_encoding=False)
        encoding = mgc_encoding.from_file(filename)
        info = mgc_string.from_file(filename)
        return (encoding, info)

    def _process_xls(self, resource_id):
        ssconvert_call = ["ssconvert", #from gnumeric package
                          "-T",
                          "Gnumeric_stf:stf_csv",
                          csv2rdf.config.config.resources_path + resource_id,
                          csv2rdf.config.config.resources_path + resource_id]
        pipe = subprocess.Popen(ssconvert_call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pipe_message_stdout = pipe.stdout.read()
        pipe_message_stderr = pipe.stderr.read()
        logging.debug(pipe_message_stdout)
        logging.error(pipe_message_stderr)

    def _process_archive(self, filename):
        sevenza_call = ["7za",
                          "l",
                          csv2rdf.config.config.resources_path + filename]
        pipe = subprocess.Popen(sevenza_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        logging.debug(pipe_message)
        pattern = "(\d+) files"
        number_of_files = re.search(pattern, pipe_message)
        number_of_files = int(number_of_files.group(0).split()[0])
        logging.debug("Number of files identified: %d" % number_of_files)
        if(number_of_files < 2):
            #get the file name
            pattern = "\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+.{5}\s+\d+\s+\d+\s+(.*)\n"
            original_filename = re.search(pattern, pipe_message)
            original_filename = original_filename.group(0).split()[-1]
            #extract
            sevenza_call = ["7za",
                            "e",
                            csv2rdf.config.config.resources_path + filename]
            pipe = subprocess.Popen(sevenza_call, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            #move to original
            mv_call = ["mv",
                       csv2rdf.config.config.resources_path + original_filename,
                       csv2rdf.config.config.resources_path + filename]
            pipe = subprocess.Popen(mv_call, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            logging.debug(pipe_message)
        else:
            #more than 1 file in the archive
            logging.debug("Resource %s is an archive and has > 1 files inside, deleting." % self.id)
            self.delete()

    def _process_utf16(self, filename):
        f_in = open(filename, 'rU')
        f_out = open(filename+"-converted", 'wb')

        for piece in self._read_in_chunks(f_in):
            converted_piece = piece.decode('utf-16-le', errors='ignore')
            converted_piece = converted_piece.encode('ascii', errors='ignore')
            f_out.write(converted_piece)

        f_in.close()
        f_out.close()

        #move converted to original
        mv_call = ["mv",
                    filename+"-converted",
                    filename]
        pipe = subprocess.Popen(mv_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        logging.debug(pipe_message)

    def _read_in_chunks(self, file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def get_csv_resource_list_local(self):
        """
            Returns the list of downloaded csv CKAN resources (csv files)
        """
        csv_list = os.listdir(csv2rdf.config.config.resources_path)
        return csv_list

if __name__ == '__main__':

    #Case 1: good CSV file
    #tabular_file = TabularFile('2daa0e60-4c36-487d-bb29-b3eba4e5ff0e')
    #tabular_file.download()
    #tabular_file.validate()

    #Delete cases
    #mswordbinary:
    #tabular_file = TabularFile('46b54553-eb4d-470b-9dae-f45d05a2bfdc')
    #tabular_file.download()
    #tabular_file.validate()
    ##Composite Document.*No summary
    #tabular_file = TabularFile('8a736d1c-e74f-473c-b299-26535bac56f1')
    #tabular_file.download()
    #tabular_file.validate()
    ##BitTorrent
    #tabular_file = TabularFile('2b25aaf9-ad77-489e-9b30-c6da311dd990')
    #tabular_file.download()
    #tabular_file.validate()
    ##PDF
    #tabular_file = TabularFile('cd23c58d-8bf4-443f-ac2d-678e37c835d2')
    #tabular_file.download()
    #tabular_file.validate()
    ##XML
    #tabular_file = TabularFile('f3dc8c6a-f0cd-4004-8a14-ed9f2ebc337c')
    #tabular_file.download()
    #tabular_file.validate()
    ##HTML
    #tabular_file = TabularFile('e278f3c9-a038-40bd-8e9b-c055bb551de6')
    #tabular_file.download()
    #tabular_file.validate()

    #Excel cases
    #tabular_file = TabularFile('938266d1-d453-4c46-901a-2f0dc91daaac')
    #tabular_file.download()
    #tabular_file.validate()
    #tabular_file = TabularFile('96129c64-e4a8-49d1-928b-24c16944d5b3')
    #tabular_file.download()
    #tabular_file.validate()
    #tabular_file = TabularFile('033f30af-e509-423d-8a27-958df9bbb15d')
    #tabular_file.download()
    #tabular_file.validate()
    #tabular_file = TabularFile('108fd45b-bda5-4ad7-9c6b-f26704447b5f')
    #tabular_file.download()
    #tabular_file.validate()
    #tabular_file = TabularFile('00b4658d-3783-4f6b-b0b8-0c3b08d7f731')
    #tabular_file.download()
    #tabular_file.validate()

    #Archives
    #gzip
    tabular_file = TabularFile('9a54203b-1ac1-43ef-b93d-ba29bbd4db6a')
    tabular_file.download()
    tabular_file.validate()
    #tarbinary
    tabular_file = TabularFile('1d3fe6f0-9c5a-45a9-9418-89ad4a672bea')
    #7-zip
    tabular_file = TabularFile('b8ba97d5-4661-46a7-b055-366e865a7c13')
    #Zip
    tabular_file = TabularFile('92d1fa6a-3f89-441d-ab98-8ea65ba34f24')

    #UTF-8
    tabular_file = TabularFile('bb3e753c-e27a-48cf-9488-e2d9c85e55ea')
    tabular_file = TabularFile('c9c6f5f1-a89d-4e3c-9fa6-940d42f61212')
    #UTF-16LE
    tabular_file = TabularFile('63b159d7-90c5-443b-846d-f700f74ea062')
    tabular_file = TabularFile('c3585646-d1f3-4555-9286-79ed8c9b7f5f')

    #tabular_file = TabularFile('1aa9c015-3c65-4385-8d34-60ca0a875728')
    #print tabular_file.get_csv_file_url()
    #print tabular_file.download()
    #print tabular_file.delete()
    #print tabular_file.get_csv_file_path()
    #print tabular_file.read_resource_file()
    #header_position = tabular_file.get_header_position()
    #print tabular_file.extract_header(header_position)
    #print tabular_file.validate()
