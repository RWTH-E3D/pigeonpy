from pathlib import Path

from pigeonpy.study.study import Study
from pigeonpy.data.epddata.source.oekobaudatapi import OekobaudatApi
from pigeonpy.epd.epddataset.en15804A2dataset import En15804A2Dataset
from visualization import plot_ap_overview, plot_weighted_score_bar, plot_reference_flow_bar, plot_indicators_bar

# ---- Study setup ----
input_csv_path = Path.cwd() / "calculationinput.csv"

example_study = Study(
    study_name="wooden consturctions dataholz",
    environmental_indicators=["gwp-total", "ap"],
    life_cycle_stages=["a1_a3","a4", "a5", "c1", "c2", "c3", "c4"],
    observation_period=50,
    dataset_template=En15804A2Dataset
)
example_study.epd_datamanager.register_source("oekobaudat API", OekobaudatApi())
example_study.load_calculation_input(input_csv_path, sep=";")

partition_keys = [
    ("Dataholz ID", "Dataholz insulation option", "Datatype"),
    ("Dataholz ID", "Dataholz insulation option", "Load-bearing"),
    ("Dataholz ID", "Dataholz insulation option", "Insulation"),
    ("Dataholz ID", "Dataholz insulation option", "Material class"),
    ("Dataholz ID", "Dataholz insulation option"),
]

example_study.run_calculation(*partition_keys)

reference_normalize = {"gwp-total": 9.22E+03,
                       "ap": 4.73E+01}

weighting_factors = {"gwp-total": 0.6,
                     "ap": 0.4}

example_study.normalize("JRC-EC EU27", reference_normalize)
example_study.weight("Example preference", weighting_factors, normalization_method="JRC-EC EU27")

weighted_results = example_study.result["Example preference"][("Dataholz ID", "Dataholz insulation option")]

u_values = {
    ("awmopo04a", "00"): 0.21,
    ("awmopo04a", "01"): 0.21,
    ("awmopo04a", "02"): 0.21,
    ("awmopo04a", "03"): 0.17,
    ("awmopo04a", "04"): 0.17,
    ("awmopo04a", "05"): 0.17,
    ("awropo09a", "00"): 0.2,
    ("awropo09a", "03"): 0.15,
    ("awropo09a", "06"): 0.2,
    ("awropo09a", "11"): 0.2,
    ("awropo09a", "16"): 0.15,
    ("awropo09a", "17"): 0.15,
}

result_reference_flow = {}

for key in u_values:
    result_reference_flow[key] = weighted_results[key].get_sum().sum() / (u_values[key]**-1)

# ---- Show calculation history ----
weighted_results[("awmopo04a", "00")].show_history()

# ---- Visualization ----

partition_keys_visualization = [
   ("Dataholz ID", "Dataholz insulation option", "Datatype"),
   ("Dataholz ID", "Dataholz insulation option", "Load-bearing"),
   ("Dataholz ID", "Dataholz insulation option", "Insulation"),
   ("Dataholz ID", "Dataholz insulation option", "Material class"),
]

plot_weighted_score_bar(example_study, result_reference_flow, u_values, save_path=f"{Path.cwd() / 'weighted_score_bar.svg'}", save_format="svg")
plot_reference_flow_bar(example_study, result_reference_flow, u_values, save_path=f"{Path.cwd() / 'reference_flow_bar.svg'}", save_format="svg")
plot_indicators_bar(example_study, result_reference_flow, save_path=f"{Path.cwd() / 'indicators_bar.svg'}", save_format="svg")
plot_ap_overview(example_study, partition_keys_visualization, save_path=f"{Path.cwd() / 'ap_overview.svg'}", save_format="svg")

