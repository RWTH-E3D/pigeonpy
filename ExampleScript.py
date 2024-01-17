from logic.epddataset.en15804A1dataset import En15804A1Dataset
from data.dataclass import DataClass

"""Momentan nur für En15804+A1 Standard"""

"""Bsp. für teco json"""
dataclass_teco_json = DataClass()

# Bsp.: Holzfaserdämmstoff: d601d54e-a2eb-42bb-b32b-c59d1b2332a9 (a1,a2,a3...)
holzfaser_dataset = En15804A1Dataset()
holzfaser_dataset.load_lca_dataset("d601d54e-a2eb-42bb-b32b-c59d1b2332a9", dataclass_teco_json)
# Bsp.: Laubschnittholz getrocknet (Durchschnitt DE): 596f1878-75cf-4cd4-a510-003a67094dd7 (a1,a2,a3,a1_a3...)
laubschnitt_dataset = En15804A1Dataset()
laubschnitt_dataset.load_lca_dataset("596f1878-75cf-4cd4-a510-003a67094dd7", dataclass_teco_json)

added_dataset = holzfaser_dataset + laubschnitt_dataset
subtracted_dataset = holzfaser_dataset - laubschnitt_dataset
multiplied_dataset = holzfaser_dataset * laubschnitt_dataset
multiplied_with_scalar = holzfaser_dataset * 5
divided_dataset = holzfaser_dataset / 2


"""Bsp. für CSV"""
dataclass_csv = DataClass(file_format="csv")

# Bsp. Laubschnittholz getrocknet (Durchschnitt DE): 596f1878-75cf-4cd4-a510-003a67094dd7
laubschnitt_dataset_csv = En15804A1Dataset()
laubschnitt_dataset_csv.load_lca_dataset("596f1878-75cf-4cd4-a510-003a67094dd7", dataclass_csv)
# Bsp. Zellulosefaserplatten: cf963fcb-0e03-48c0-b501-ad0d1e3c22c0
zellulose_dataset = En15804A1Dataset()
zellulose_dataset.load_lca_dataset("cf963fcb-0e03-48c0-b501-ad0d1e3c22c0", dataclass_csv)

added_dataset_csv = laubschnitt_dataset_csv + zellulose_dataset
subtracted_dataset_csv = laubschnitt_dataset_csv - zellulose_dataset
multiplied_dataset_csv = laubschnitt_dataset_csv * zellulose_dataset
multiplied_dataset_scalar_csv = laubschnitt_dataset_csv * 2
divided_dataset_csv = laubschnitt_dataset_csv/2

print(laubschnitt_dataset_csv)
print(added_dataset_csv)
