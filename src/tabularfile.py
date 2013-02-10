class TabularFile():
    def __init__(self, resource_id):
        self.id = resource_id
        self.filename = self.id
    
    def download_all_resources(self):
        db = Database(self.resource_dir)
        for resource in self.resources:
            url = resource['url']
            filename = self.extract_filename_url(url)
            try:
                r = requests.get(url, timeout=self.timeout)
                db.saveDbaseRaw(filename, r.content)
            except BaseException as e:
                print "Could not get the resource " + str(resource['id']) + " ! " + str(e)
    
    def validate(self):
        """ Destructive, be careful to use
            TODO: include html, xml check (see scripts)
        """
        filename = config.resources_path + self.filename
        mgc_encoding = magic.Magic(mime=False, magic_file=None, mime_encoding=True)
        mgc_string = magic.Magic(mime=False, magic_file=None, mime_encoding=False)
        encoding = mgc_encoding.from_file(filename)
        info = mgc_string.from_file(filename)
        if(encoding == "utf-16le"):
            self._process_utf16(filename)
        elif(re.match("^binary", encoding) or
             re.match("^application/.*", encoding)):
            self._process_based_on(info, filename)
        else:
            return True
            
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
            
    def _delete(self, filename):
        rm_call = ["rm", filename]
        pipe = subprocess.Popen(rm_call, stdout=subprocess.PIPE)
        pipe_message = pipe.stdout.read()
        
    def get_csv_file_path(self):
        if(os.path.exists(config.resources_path + self.filename)):
            return config.resources_path + self.filename
        else:
            self._download()
            return config.resources_path + self.filename
        
    def _download(self):
        try:
            r = requests.get(self.url, timeout=config.ckan_request_timeout)
            assert r.ok, r
            file = Database(config.resources_path)
            file.saveDbaseRaw(self.filename, r.content)
            return "resource " + str(self.id) + " status_code " + str(r.status_code) + "\n"
        except BaseException as e:
            return "Could not download the resource "+str(self.id)+" ! "+str(e)+"\n"
            
    def get_csv_file_url(self):
        return str(self.server_base_url) + str(self.resource_dir) + str(self.filename)
        
    def _extract_csv_header_and_position_first_line(self):
        """
            This function take the first line of the csv file
            as a header. Should work in 60% of all cases.
        """
        with open(self.resource_dir + self.filename, 'rU') as csvfile:
            #dialect does not work good!
            #dialect = csv.Sniffer().sniff(csvfile.read(1024))
            #csvfile.seek(0)
            reader = csv.reader(csvfile)
            try:
                for row in reader:
                    return row
            except BaseException as e:
                print str(e)
                return []
            #print csv.Sniffer().has_header(csvfile.read(1024))
            #csvfile.seek(0)
            
    def read_resource_file(self):
        try:
            file = Database(config.resources_path)
            return file.loadDbaseRaw(self.filename)
        except IOError as e:
            # [Errno 2] No such file or directory
            if(e.errno == 2):
                self._download()
                self.read_resource_file()
        except BaseException as e:
            print "Could not read the resource! " + str(e)