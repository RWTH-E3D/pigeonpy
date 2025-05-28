from data.epddata.source.epdsource import EpdSource


class FileEpdSource(EpdSource):

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
