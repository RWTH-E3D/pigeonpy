import pandas as pd

class calculator(object):

    def __init__(self):
        self._calculation_header = ["calculation_id", "value", "epd_uuid", "epd_name", "comment"]
        dummy_data_calc = [[0,1, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [1, 3, "cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", "", ""],
                           [2, 44, "c8835af8-44d2-47df-a833-8e823e6ee5cd", "", ""],
                           [3, 2, "9099dfdd-22a6-4dee-9b60-0e90701e9d99", "", ""]]
        self._calculation_df = pd.DataFrame(dummy_data_calc, columns=self._calculation_header)

        dummy_data_cat = [[0, "1993", 0],
                          [1, "1993", 0],
                          [2, "1994", 0],
                          [3, "1995", 0],
                          [0, "test", 1],
                          [1, "test", 1],
                          [2, "test3", 1],
                          [3, "test4", 1],
                          [0, "Bauteil1", 2],
                          [1, "Bauteil1", 2],
                          [2, "Bauteil1", 2],
                          [3, "Bauteil2", 2]
                          ]
        self._category_header = ["calculation_id", "category_name", "categorization_id"]
        self._category_df = pd.DataFrame(dummy_data_cat, columns=self._category_header)

        dummy_data_catz = [[0, "Jahr"],
                           [1, "Typ"],
                           [2, "Bauteil"]]
        self._categorization_header = ["categorization_id", "categorization_name"]
        self._categorization_df = pd.DataFrame(dummy_data_catz, columns=self._categorization_header)

    def _select_by_categorization(self, *categorizations):

        if len(categorizations) == 1:
            categorization = categorizations[0]
            catz_df = self._categorization_df[self._categorization_df['categorization_name'] == categorization]
            cat_df = pd.merge(self._category_df, catz_df, on="categorization_id", how='inner')
            calc_df = pd.merge(self._calculation_df, cat_df, on="calculation_id", how='inner')
        else:
            cat_df = self._category_df.merge(self._categorization_df, on='categorization_id')
            pivot_df = cat_df.pivot(index='calculation_id', columns='categorization_name',
                                       values='category_name').reset_index()
            pivot_df['category_name'] = pivot_df[list(categorizations)].apply(tuple, axis=1)
            calc_df = self._calculation_df.merge(pivot_df, on='calculation_id', how='left').fillna('')



        return calc_df







    def calculate(self, *categorizations):
        pass


test = calculator()
print(test._select_by_categorization("Jahr", "Typ", "Bauteil")[["value", "epd_uuid", "category_name"]])