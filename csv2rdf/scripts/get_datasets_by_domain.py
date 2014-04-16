import cPickle
#import datetime
from csv2rdf.config.config import data_path
#date_now = str(datetime.datetime.now().strftime("%d%B%Y"))
filename = "tags"
filepath = data_path + filename
tags = cPickle.load(open(filepath, 'r'))

import operator
sorted_tags = sorted(tags.iteritems(), key=operator.itemgetter(1), reverse=True)

print sorted_tags[0:40]
