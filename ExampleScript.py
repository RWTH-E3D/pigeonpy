import time
from study.study import Study
from pathlib import Path
from data.epddata.source.oekobaudatapi import OekobaudatAPI
from epd.epddataset.en15804A2dataset import En15804A2Dataset

import numpy as np # Löschen, wenn Gewichtungsfaktoren über Funktion erstellt werden
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


tic = time.time()

#input file wird geladen
input_csv_path = Path.cwd() / "data" / "input" / "inputdata" / "input_csv_paper+service_life+headers.csv"

# Studie wird erstellt
standard_dataset = En15804A2Dataset
example_study = Study(
    study_name="example_study",
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

#Normalisieurngs EPD wird geladen
normalization_epd = En15804A2Dataset()
normalization_epd.load_lca_dataset("f8ff7cbf-f3bb-4499-95e2-8268dd84fab1", example_study.epd_datamanager)

# Normalization
normalization_factors = {
    "gwp-total": 9220,
    "odp": 0.022,
    "pocp": 31.7
}
# Benennung der Normalisierung
example_study.lcia.normalize("test_normalization", normalization_factors)

# Weighting
weighting_factors = {
    "gwp-total": 0.33,
    "odp": 0.33,
    "pocp": 0.34
}
# Benennung der Gewichtung
example_study.lcia.weight("test_weighting", weighting_factors, normalization_method="test_normalization")



###########################################################################
############################## Visualisation ##############################
###########################################################################

# Daten sammeln
print('example_study.lcia.weighted_results["test_weighting"]["Total result"]: ', example_study.lcia.weighted_results["test_weighting"]["Total result"])

life_cycle_stages=["a1_a3", "c1", "c2", "c3", "c4", "d"]                        #"b6",
environmental_indicators=["gwp-total", "odp", "pocp"]

#data = example_study.lcia.weighted_results["test_weighting"]["Total result"]

# Dictionary zur Speicherung der Ergebnisse
results = {}
colums = ['environmental_indicator', 'numerical_value', 'life_cycle_stage']
df = pd.DataFrame(columns=colums)

# Iteration über die Umweltindikatoren
for stage in life_cycle_stages:
    # Neue Liste für den aktuellen life_cycle_stage im Dictionary erstellen
    results[stage] = []  # Leere Liste für jeden stage
    #print("stage: ", stage)

    # Iteration über die Lebenszyklusphasen
    for indicator in environmental_indicators:
        value = example_study.lcia.weighted_results["test_weighting"]["Total result"].get(indicator, stage)
        #print("indicator: ", indicator)
        results[stage].append(value)
        new_index = len(df)
        df.loc[new_index] = [indicator, value, stage]

# c1_c4 berechnen und an DataFrame anfügen
for indicator in environmental_indicators:
    filtered_df = df[(df['environmental_indicator'] == indicator) & (df['life_cycle_stage'].isin(['c1', 'c2', 'c3', 'c4']))]

    # Werte für c1 bis c4 aufsummieren
    sum = filtered_df['numerical_value'].sum()

    new_row_df = pd.DataFrame([{'environmental_indicator' : indicator,
                    'numerical_value' : sum,
                    'life_cycle_stage' : 'c1_c4'}])

    df = pd.concat([df, new_row_df], ignore_index=True)

# Zeilen mit C1, C2, c3, und c4 löschen (nur noch c1_c4 behalten)
for c in ['c1', 'c2', 'c3', 'c4']:
    df = df[df['life_cycle_stage'] != c]
print("df: ", df)

print("df: ", df)


#print("Die Summe der gwp-total Werte für c1, c2 und c3 ist:", sum_gwp_total)


"""
# Ausgabe der Ergebnisse für jeden Indikator
for indicator, gwp_total in results.items():
    print(f"Werte für {indicator}: {gwp_total}")
"""
"""
# Für Gruppierung nach Umweltindikatoren anstatt nach Life Cycle Stages
# Iteration über die Umweltindikatoren
for indicator in environmental_indicators:
    # Neue Liste für den aktuellen Indikator im Dictionary erstellen
    results[indicator] = []  # Leere Liste für jeden Indikator

    # Iteration über die Lebenszyklusphasen
    for stage in life_cycle_stages:
        wert = example_study.lcia.weighted_results["test_weighting"]["Total result"].get(indicator, stage)
        results[stage].append(wert)

# Ausgabe der Ergebnisse für jeden Indikator
for indicator, gwp_total in results.items():
    print(f"Werte für {indicator}: {gwp_total}")"""

print("results: ", results)

# Anzahl der Indikatoren und Lebenszyklusphasen
num_indicators = len(environmental_indicators)
num_stages = len(life_cycle_stages)


# The following is a helper function that given the angle at which the bar is positioned and the offset used in the barchart, determines the rotation and alignment of the labels.
def get_label_rotation(angle, offset):
    # Rotation must be specified in degrees :(
    rotation = np.rad2deg(angle + offset)
    if angle <= np.pi:
        alignment = "right"
        rotation = rotation + 180
    else:
        alignment = "left"
    return rotation, alignment


# This is the function that actually adds the labels (with ax.text()) to the plot:
def add_labels(angles, values, labels, offset, ax):
    # This is the space between the end of the bar and the label
    padding = 4

    # Iterate over angles, values, and labels, to add all of them.
    for angle, value, label, in zip(angles, values, labels):
        angle = angle

        # Obtain text rotation and alignment
        rotation, alignment = get_label_rotation(angle, offset)

        # And finally add the text
        ax.text(
            x=angle,
            y=value + padding,
            s=label,
            ha=alignment,
            va="center",
            rotation=rotation,
            rotation_mode="anchor"
        )


# All this part is like the code above
# First of all, let's create ANGLES, which give the positions where bars are located. The numerical_value array contains the heights of the bars, and environmental_indicator stores the labels.
numerical_value = df["numerical_value"].values
environmental_indicator = df["environmental_indicator"].values
life_cycle_stage = df["life_cycle_stage"].values

# Determines where to place the first bar.
# By default, matplotlib starts at 0 (the first bar is horizontal)
# but here we say we want to start at pi/2 (90 deg)
OFFSET = np.pi / 2

PAD = 3
ANGLES_N = len(numerical_value) + PAD * len(np.unique(life_cycle_stage))
ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
# Determine the width of each bar.
# The circumference is '2 * pi', so we divide that total width over the number of bars.
WIDTH = (2 * np.pi) / len(ANGLES)

GROUPS_SIZE = [len(i[1]) for i in df.groupby("life_cycle_stage")]

offset = 0
IDXS = []
for size in GROUPS_SIZE:
    IDXS += list(range(offset + PAD, offset + size + PAD))
    offset += size + PAD

fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={"projection": "polar"})
#fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={"projection": "3d"})
ax.set_theta_offset(OFFSET)
#ax.set_ylim(-100, 100)
#ax.set_frame_on(False)
ax.xaxis.grid(False)
ax.yaxis.grid(False)
ax.set_xticks([])
ax.set_yticks([])

#GROUPS_SIZE = [len(i[1]) for i in df.groupby("group")]
COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

ax.bar(
    ANGLES[IDXS], numerical_value, width=WIDTH, color=COLORS,
    edgecolor="white", linewidth=2
)

add_labels(ANGLES[IDXS], numerical_value, environmental_indicator, OFFSET, ax)

# Extra customization below here --------------------

# This iterates over the sizes of the groups adding reference
# lines and annotations.

group_names = np.unique(life_cycle_stage)

offset = 0
for group, size in zip(group_names, GROUPS_SIZE):
    # Add line below bars
    x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
    ax.plot(x1, [-5] * 50, color="#333333")

    # Add text to indicate group
    ax.text(
        np.mean(x1), -20, group, color="#333333", fontsize=14,
        fontweight="bold", ha="center", va="center"
    )

    # Add reference lines at 20, 40, 60, and 80
    x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
    ax.plot(x2, [20] * 50, color="#bebebe", lw=0.8)
    ax.plot(x2, [40] * 50, color="#bebebe", lw=0.8)
    ax.plot(x2, [60] * 50, color="#bebebe", lw=0.8)
    ax.plot(x2, [80] * 50, color="#bebebe", lw=0.8)

    # 3D Plot
    #x3 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)

    offset += size + PAD

plt.show()
plt.savefig("Visualisation.svg", format='svg')











toc = time.time()
print('dynamic lca draft run in', round((toc - tic), 2), 'seconds')



