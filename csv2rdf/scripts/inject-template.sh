#!/bin/bash

find ../../files/csv/ -type f -size -1024k > lessthanonemb.list
python inject-template.py
rm lessthanonemb.list
