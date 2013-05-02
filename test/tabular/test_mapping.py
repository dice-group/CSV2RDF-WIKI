from tabular.mapping import Mapping
from test import config

class TestMapping():
    def __init__(self):
        self.mapping = Mapping(config.resource_id)

    def test_request_wiki_page(self):
        wikipage = self.mapping.request_wiki_page()
        print wikipage
        assert wikipage

    def test_myoutput(capsys): # or use "capfd" for fd-level
        print ("hello")
        sys.stderr.write("world\n")
        out, err = capsys.readouterr()
        assert out == "hello\n"
        assert err == "world\n"
        print "next"
        out, err = capsys.readouterr()
        assert out == "next\n"

if __name__ == "__main__":
    test = TestMapping()

