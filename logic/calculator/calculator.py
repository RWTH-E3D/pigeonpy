import pandas as pd

class calculator(object):

    def __init__(self):
        self._calculation_table_headers = ["value", "epd_uuid", "epd_name", "comment"]
        dummy_data = [1, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""]
        self._calculation_table = pd.DataFrame(data, columns=self._calculation_table_headers)
