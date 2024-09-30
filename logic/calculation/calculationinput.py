from logic.calculation.calculator import Calculator
import pandas as pd

class CalculationInput(object):
    def __init__(self):
        self._calculation_header = ["calculation_id", "value", "epd_uuid", "epd_name", "comment"]
        self._category_header = ["calculation_id", "category_name", "categorization_id"]
        self._categorization_header = ["categorization_id", "categorization_name"]
        self.calculation_df = None
        self.category_df = None
        self.categorization_df = None

    def load(self, filepath):
        """Method to set the class attributes (dataframes with calculation info, categorizations, categories)
        based on the input csv

        Parameters
        ----------
        path: str
            Path to the input csv file
        """

        #Todo: extend load function, so that not only the uuid is stored in the input dataframe, but the epdfataobject
        #       itself

        import_df = (pd.read_csv(filepath, sep=',', encoding='ANSI'))
        import_df['UUID'] = import_df['UUID'].str.strip()

        catigorizations = [[idx, col] for idx, col in enumerate(import_df.columns[4:11])]
        categories = []
        calculations = []

        for idx, row in import_df.iloc[:, :4].iterrows():
            calculations.append([idx] + row.tolist())

        for col_idx, col_name in catigorizations:
            col_values = import_df.iloc[:, col_idx + 4]
            for idx, val in enumerate(col_values):
                categories.append([idx, val, col_idx])

        self.calculation_df = pd.DataFrame(calculations, columns=self._calculation_header)
        self.category_df = pd.DataFrame(categories, columns=self._category_header)
        self.categorization_df = pd.DataFrame(catigorizations, columns=self._categorization_header)

    def _select_by_categorization(self, *categorizations):
        """Method to create a dataframe for the calculation which additionally contains the category or category
        combination according to which the datasets will be calculated.

        Parameters
        ----------
        *categorizations: str
            The category names as strings according to which the calculation will be made

        Returns
        -------
        calc_df: pd.DataFrame
            Contains information for the calculation; UUIDs, amounts, category/ categories
        """

        if len(categorizations) == 1:
            categorization = categorizations[0]
            catz_df = self.categorization_df[self.categorization_df['categorization_name'] == categorization]
            cat_df = pd.merge(self.category_df, catz_df, on="categorization_id", how='inner')
            calc_df = pd.merge(self.calculation_df, cat_df, on="calculation_id", how='inner')
        else:
            categorization = ' '.join(categorizations)
            cat_df = self.category_df.merge(self.categorization_df, on='categorization_id')
            pivot_df = cat_df.pivot(index='calculation_id', columns='categorization_name',
                                    values='category_name').reset_index()
            pivot_df['category_name'] = pivot_df[list(categorizations)].apply(tuple, axis=1)
            calc_df = self.calculation_df.merge(pivot_df, on='calculation_id', how='left').fillna('')
            calc_df.insert(2, "categorization_name", categorization)

        return calc_df

