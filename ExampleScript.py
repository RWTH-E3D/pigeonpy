from logic.epddataset.en15804A1dataset import En15804A1Dataset
from logic.epddataset.en15804A2dataset import En15804A2Dataset
from data.dataclass import DataClass
#from logic.calculator.calculator import Calculator
import data.output.lca_data_output as lca_data_output
import utility as utility
from project import Project


"""
Bsp. für teco json (enthält nur A1 Datensätze):

    Default file_format = 'teco_json' für A1, wenn keine DataClass Instanz übergeben wird
    --> Datensätze, die nur in csv vorhanden sind können nur geladen werden, wenn DataClass Instanz übergeben wird

"""

dataclass_teco_json = DataClass()

# Bsp.: Holzfaserdämmstoff: d601d54e-a2eb-42bb-b32b-c59d1b2332a9 (a1,a2,a3...)
holzfaser_dataset_a1 = En15804A1Dataset()
holzfaser_dataset_a1.load_lca_dataset("d601d54e-a2eb-42bb-b32b-c59d1b2332a9", dataclass_teco_json)

# Bsp.: Laubschnittholz getrocknet (Durchschnitt DE): 596f1878-75cf-4cd4-a510-003a67094dd7 (a1,a2,a3,a1_a3...)
# Laden ohne übergebene DataClass Instanz
laubschnitt_dataset_a1 = En15804A1Dataset()
laubschnitt_dataset_a1.load_lca_dataset("596f1878-75cf-4cd4-a510-003a67094dd7")



"""
Bsp. für CSV und Standard A1:
    
    Kein Laden von Datensätzen aus csv ohne übergebene DataClass Instanz möglich, siehe Beschreibung für teco_json

"""

dataclass_csv = DataClass(file_format="csv")

# Bsp. Laubschnittholz getrocknet (Durchschnitt DE): 596f1878-75cf-4cd4-a510-003a67094dd7
laubschnitt_dataset_csv_a1 = En15804A1Dataset()
laubschnitt_dataset_csv_a1.load_lca_dataset("596f1878-75cf-4cd4-a510-003a67094dd7", dataclass_csv)

# Bsp. Zellulosefaserplatten: cf963fcb-0e03-48c0-b501-ad0d1e3c22c0
zellulose_dataset_a1 = En15804A1Dataset()
zellulose_dataset_a1.load_lca_dataset("cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", dataclass_csv)

added_dataset_csv_a1 = laubschnitt_dataset_csv_a1 + zellulose_dataset_a1
subtracted_dataset_csv_a1 = laubschnitt_dataset_csv_a1 - zellulose_dataset_a1
multiplied_dataset_csv_a1 = laubschnitt_dataset_csv_a1 * zellulose_dataset_a1
multiplied_dataset_scalar_csv_a1 = laubschnitt_dataset_csv_a1 * 2
divided_dataset_csv_a1 = laubschnitt_dataset_csv_a1/2

# Verrechnen von Datensätzen aus unterschiedlichen Quellen
added_dataset_tecojson_csv_a1 = holzfaser_dataset_a1 + zellulose_dataset_a1

print(zellulose_dataset_a1.get("gwp", "a1_a3"))

print(zellulose_dataset_a1.get_sum("gwp", "d"))

print(zellulose_dataset_a1)



"""
Bsp. für csv und Standard A2:

    Default file_format = 'csv' für Standard A2
    Rechnen mit Datensätzen analog zu Standard A1
    
"""

dataclass_csv_a2 = DataClass(used_standard="A2", file_format="csv")

# Bsp. Hobelware (Durchschnitt DE): 4ef9fd61-0aae-45e0-abcb-7573b4b05408 (a1,a2,a3,a1_a3)
Hobelware_dataset_a2 = En15804A2Dataset()
Hobelware_dataset_a2.load_lca_dataset("4ef9fd61-0aae-45e0-abcb-7573b4b05408", data_class=dataclass_csv_a2)

# Bsp. Mitteldichte Faserplatte (Durchschnitt DE): 8bd1172b-b81f-4805-a77e-1534b5f6bdee (a1_a3,a1,a2,a3)
# Laden ohne übergebene DataClass Instanz
Faserplatte_dataset_a2 = En15804A2Dataset()
Faserplatte_dataset_a2.load_lca_dataset("8bd1172b-b81f-4805-a77e-1534b5f6bdee")



"""
Beispiel für Berechnung und Export
"""
"""
example = Calculator()

example.import_calculation("C:\\Users\\J.K. Rollerblade\\PycharmProjects\\dynamic_lca_draft\\data\\input\\inputdata\\input_data_dynamic_csv_V2.CSV")
calculated_dataframe = example.calculate("Category1","Year Installation for components or occurence for consumption")

lca_data_output.export_calculated_dataframe(df=calculated_dataframe, file_format="teco_json")
# default file_format ist csv, default drop_rows=False, default path/ Dateiname ist output Ordner vom Projekt/ lca_data_export.csv
lca_data_output.export_calculated_dataframe(df=calculated_dataframe)
lca_data_output.export_calculated_dataframe(df=calculated_dataframe,
                                            path="C:\\Users\\J.K. Rollerblade\\PycharmProjects\\dynamic_lca_draft\\data\\output\\lca_data_export_drop_rows.csv",
                                            drop_rows=True)

Faserplatte_dataset_a2.export(drop_rows=True)
Faserplatte_dataset_a2.export(file_format="teco_json")

print(calculated_dataframe[("Technical building equipment", 1996)])
"""


"""
Beispiel für Interpolation
"""
# Only for example datasets
import numpy as np

example_dataset1 = En15804A1Dataset()
example_dataset1._data = np.full((25, 18), 2021)
example_dataset2 = En15804A1Dataset()
example_dataset2._data = np.full((25, 18), 2030)

list_of_interpolation_results = utility.linear_interpolate(example_dataset1, example_dataset2, 9, return_datasets=False)
print(list_of_interpolation_results[0])



"""
Beispiel für Interaktion mit Project Class
"""

input_csv_path = "C:\\Users\\J.K. Rollerblade\\PycharmProjects\\dynamic_lca_draft\\data\\input\\inputdata\\input_data_dynamic_csv_V2.CSV"

test = Project()
test._name = "Test_project"

test.add_calculation("2 Single Categorizations", input_csv_path, "Category1", "Year Disposal")
test.add_calculation("Test calculation", input_csv_path)
test.remove_calculation("Test calculation")

test.add_calculation("Tuple Categorization", input_csv_path)
test.add_categorization("Tuple Categorization", "test123", ("Category1","Year Installation for components or occurence for consumption"), "test456")
test.remove_categorization("Tuple Categorization", "test456", "test123")

test.calculate_all()
#test.export_results(all_results=True)

temp = test.results['2 Single Categorizations']['Category1']["Foundation"]
print(temp)
