import pandas as pd

class calculator(object):

    def __init__(self):
        self._calculation_table_header = ["calculation_id", "value", "epd_uuid", "epd_name", "comment"]
        dummy_data_calc = [[0,1, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [1, 3, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [2, 44, "c8835af8-44d2-47df-a833-8e823e6ee5cd", "", ""],
                           [3, 2, "9099dfdd-22a6-4dee-9b60-0e90701e9d99", "", ""]]
        self._calculation_table = pd.DataFrame(dummy_data_calc, columns=self._calculation_table_headers)

        dummy_data_cat = [[0, "1993", 0],
                          [1, "1993", 0],
                          [2, "1994", 0],
                          [3, "1995", 0]]
        self._category_name = ["calculation_id", "name", "categorization_id"]
        self._category_table = pd.DataFrame(dummy_data_cat, columns=self._category_name)

        dummy_data_calc = [0, "Jahr"]
        self._categorization_header = ["categorization_id", "name"]
        self._categorization_table = pd.DataFrame(dummy_data_calc, columns=self._categorization_header)


