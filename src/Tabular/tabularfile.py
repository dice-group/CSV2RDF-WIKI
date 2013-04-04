import os

import csv
import requests
from magic import Magic

import config
from database import Database
from resource import Resource


class TabularFile():
    def __init__(self, resource_id):
        self.id = resource_id
        self.filename = self.id
    
    def download(self):
        resource = Resource(self.id)
        resource.init()
        try:
            r = requests.get(resource.url, timeout=config.ckan_request_timeout)
            assert r.ok, r
            file = Database(config.resources_path)
            file.saveDbaseRaw(self.filename, r.content)
            return self.get_csv_file_path()
            #return "resource " + str(self.id) + " status_code " + str(r.status_code) + "\n"
        except BaseException as e:
            #return "Could not download the resource "+str(self.id)+" ! "+str(e)+"\n"
            return False
    
    def delete(self):
        db = Database(config.resources_path)
        db.delete(self.filename)
        return True
        
    def get_csv_file_path(self):
        db = Database(config.resources_path)
        if(db.is_exists(self.filename)):
            return db.get_path_to_file(self.filename)
        else:
            return False
        
    def get_csv_file_url(self):
        file_path = self.get_csv_file_path()
        if(file_path):
            return os.path.join(config.server_base_url, file_path)
        else:
            return False
    
    def read_resource_file(self):
        try:
            file = Database(config.resources_path)
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
        db = Database(config.resources_path)
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
        """ Destructive, be careful to use
            TODO: include html, xml check (see scripts)
        """
        (encoding, info) = self.get_info_about()
        
        #TODO: run information collection on the all files!
        #print encoding, info
        """
        if(encoding == "utf-16le"):
            self._process_utf16(filename)
        elif(re.match("^binary", encoding) or
             re.match("^application/.*", encoding)):
            self._process_based_on(info, filename)
        else:
            return True"""
    
    def get_info_about(self):
        """
            return (encoding, info) tuple
            info is a plain string and has to be parsed 
        """
        db = Database(config.resources_path)
        filename = db.get_path_to_file(self.filename)
        mgc_encoding = Magic(mime=False, mime_encoding=True)
        mgc_string = Magic(mime=False, mime_encoding=False)
        encoding = mgc_encoding.from_file(filename)
        info = mgc_string.from_file(filename)
        return (encoding, info)
            
    def _process_based_on(self, info, filename):
        """
            The order is significant here
        """
        if(re.match(".*archive.*", info)):
            self._process_archive(filename)
        elif(re.match(".*Composite Document File V2 Document.*Excel.*", info) or
           re.match(".*Microsoft Excel 2007+.*", info) or
           not re.match(".*Composite Document File V2 Document.*Word.*", info)):
            self._process_xls(filename)
        elif(re.match(".*Composite Document File V2 Document.*Word.*", info)):
            #Word document
            self._delete(filename)
            return False
            
    def _process_xls(self, resource_id):
        print resource_id
        ssconvert_call = ["ssconvert", #from gnumeric package
                          "-T",
                          "Gnumeric_stf:stf_csv",
                          resource_id,
                          resource_id]
        pipe = subprocess.Popen(ssconvert_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        self.validate()
    
    def _process_archive(self, filename):
        #unzip archive
        #check number of files
        sevenza_call = ["7za", 
                          "l",
                          filename]
        pipe = subprocess.Popen(sevenza_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        pattern = "(\d+) files"
        number_of_files = re.search(pattern, pipe_message)
        number_of_files = int(number_of_files.group(0).split()[0])
        if(number_of_files < 2):
            #get the file name
            pattern = "\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+.{5}\s+\d+\s+\d+\s+(.*)\n"
            original_filename = re.search(pattern, pipe_message)
            original_filename = original_filename.group(0).split()[-1]
            #extract
            sevenza_call = ["7za", 
                            "e",
                            filename]
            pipe = subprocess.Popen(sevenza_call, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
            #move to original
            mv_call = ["mv",
                       original_filename,
                       filename]
            pipe = subprocess.Popen(mv_call, stdout=subprocess.PIPE)
            pipe_message = pipe.stdout.read()
        else:
            #more than 1 file in the archive
            self._delete(filename)
            return False
    
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
        
    def _read_in_chunks(self, file_object, chunk_size=1024):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data
            
if __name__ == '__main__':
    tabular_file = TabularFile('1aa9c015-3c65-4385-8d34-60ca0a875728')
    print tabular_file.get_csv_file_url()
    #print tabular_file.download()
    #print tabular_file.delete()
    #print tabular_file.get_csv_file_path()
    #print tabular_file.read_resource_file()
    #header_position = tabular_file.get_header_position()
    #print tabular_file.extract_header(header_position)
    #print tabular_file.validate()
