from data.epddata.source.epdsource import EpdSource
class FileEpdSource(EpdSource):

    def __init__(self, name, filepath):
        super().__init__(name)
        self.filepath = filepath
