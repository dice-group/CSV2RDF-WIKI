#!/usr/bin/python

import os
import re

current_dir = os.getcwd()
print current_dir
files = os.listdir(current_dir)

for f in files:
    if(f.endswith('.py')):
        file_path = os.path.join(current_dir, f)
        fh = open(file_path)
        print file_path
        for line in fh.readlines():
            if(re.match(".*import.*", line)):
                print line
        fh.close()

