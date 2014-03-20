import json

class AuxilaryInterface():
    def __str__(self):
        #print self.__class__
        output = {}
        for attr, value in self.__dict__.iteritems():
            output[attr] = value
        return str(output)

    def unpack_object_to_self(self, object):
        for key in object:
            setattr(self, key, object[key])

    def extract_filename_url(self, url):
        return url.split('/')[-1].split('#')[0].split('?')[0]

    def convert_to_zero_index(self, list_one_index):
        list_zero_index = []
        for item in list_one_index:
            list_zero_index.append(item - 1)
        return list_zero_index

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class StringMatchInterface():
    def match(self, expr, string):
        import re
        pattern = re.compile(expr)
        match = pattern.match(string)
        if(match):
            return True
        else:
            return False
