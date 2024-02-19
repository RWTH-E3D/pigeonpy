from logic.epddataset.en15804A1dataset import En15804A1Dataset
from logic.epddataset.en15804A2dataset import En15804A2Dataset
from data.dataclass import DataClass


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


print(holzfaser_dataset_a1)
print(added_dataset_tecojson_csv_a1)
print(Hobelware_dataset_a2)

