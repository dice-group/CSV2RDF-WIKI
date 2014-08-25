from lovpy.lovscraper import LovScraper

class LovClassifier(object):
    def __init__(self):
        self.lovscraper = LovScraper()

    def getEntities(self, label):
        entitiesRecognized = self.lovscraper.search(label)
        return entitiesRecognized

if __name__ == "__main__":
    lovClassifier = LovClassifier()
    print lovClassifier.getEntities('Latitude')
