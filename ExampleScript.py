import time
from study.study import Study
from pathlib import Path
from data.epddata.source.oekobaudatapi import OekobaudatAPI
from epd.epddataset.en15804A2dataset import En15804A2Dataset

tic = time.time()

#input file wird geladen
input_csv_path = Path.cwd() / "data" / "input" / "inputdata" / "input_csv_paper+service_life+headers.csv"

# Studie wird erstellt
standard_dataset = En15804A2Dataset
example_study = Study(
    study_name="Doktorandenseminar",
    environmental_indicators=["gwp-total", "odp", "pocp"],
    life_cycle_stages=["a1_a3", "b6", "c1", "c2", "c3", "c4", "d"],
    observation_period=50,
    dataset_template=standard_dataset
)


oekobaudat_api = OekobaudatAPI("Ökobaudat API")

# example_study.epd_datamanager.register_source("oekobaudat", oekobaudat)
example_study.epd_datamanager.register_source("oekobaudat API", oekobaudat_api)



#Berechnung wird geladen und gestartet
example_study.load_calculation_input(input_csv_path)
example_study.run_calculation("building_type")

#print(example_study.lcia.result["building_type"]["type 1"])
#print('example_study.lcia.result["Total result"]: ', example_study.lcia.result["Total result"])
#print('example_study.lcia.result["building_type"]["type 1"]: ', example_study.lcia.result["building_type"]["type 1"])

#Normalisieurngs EPD wird geladen
normalization_epd = En15804A2Dataset()
normalization_epd.load_lca_dataset("f8ff7cbf-f3bb-4499-95e2-8268dd84fab1", example_study.epd_datamanager)

# Normalization
normalization_factors = {
    "gwp-total": 9220,
    "odp": 0.022,
    "pocp": 31.7
}
example_study.lcia.normalize("test_normalization", normalization_factors)

# Weighting
#weighting_factors = {
#    "gwp-total": 0.33,
#    "odp": 0.33,
#    "pocp": 0.34
#}
#example_study.lcia.weight("test_weighting", weighting_factors, normalization_method="test_normalization")

# Visualisation
#data = example_study.lcia.weighted_results["weighting"]["Total result"]    #["a1_a3"]
data = example_study.lcia.normalized_results["test_normalization"]["building_type"]["type 1"].data[0][1]
#data = pd.DataFrame(data)

"""

# set figure size
plt.figure(figsize=(20,10))

# plot polar axis
ax = plt.subplot(111, polar=True)

# remove grid
plt.axis('off')

# Set the coordinates limits
upperLimit = 100
lowerLimit = 0

# Compute max and min in the dataset # Änderung maximum von numpy array
#max = data['Value'].max()
max = np.max(data)
print("max: ", max)

# Let's compute heights: they are a conversion of each item value in those new coordinates
# In our example, 0 in the dataset will be converted to the lowerLimit (10)
# The maximum will be converted to the upperLimit (100)
slope = (max - lowerLimit) / max
heights = slope * data.Value + lowerLimit

# Compute the width of each bar. In total we have 2*Pi = 360°
width = 2*np.pi / len(data.index)

# Compute the angle each bar is centered on:
indexes = list(range(1, len(df.index)+1))
angles = [element * width for element in indexes]
angles

# Draw bars
bars = ax.bar(
    x=angles,
    height=heights,
    width=width,
    bottom=lowerLimit,
    linewidth=2,
    edgecolor="white")

plt.show()













"""


toc = time.time()
print('dynamic lca draft run in', round((toc - tic), 2), 'seconds')
print(example_study.lcia.result["Total result"])
print(example_study.lcia.normalized_results["test_normalization"]["Total result"])
print(example_study.lcia.normalized_results["test_normalization"]["building_type"]["type 1"])





