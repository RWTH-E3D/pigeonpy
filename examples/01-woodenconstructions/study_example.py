from study.study import Study
import copy
from pathlib import Path
from data.epddata.source.oekobaudatapi import OekobaudatApi
from epd.epddataset.en15804A2dataset import En15804A2Dataset

#input file wird geladen
input_csv_path = Path.cwd() /  "calculationinput_scenarios.csv"

standard_dataset = En15804A2Dataset
example_study = Study(
    study_name="example_study",
    environmental_indicators=["gwp-total", "odp", "ap"],
    life_cycle_stages=["a1_a3", "c1", "c2", "c3", "c4", "d"],
    observation_period=50,
    dataset_template=standard_dataset
)

oekobaudat_api = OekobaudatApi()

# example_study.epd_datamanager.register_source("oekobaudat", oekobaudat)
example_study.epd_datamanager.register_source("oekobaudat API", oekobaudat_api)

#Berechnung wird geladen und gestartet #amount;#uuid;#epd_name;#comment;#replacement_cycle;Dataholz ID;Dataholz Variant;Owner;
example_study.load_calculation_input(input_csv_path, sep=";")

selected_partitions = ("Dataholz ID", "Dataholz Variant")

example_study.run_calculation(selected_partitions)

results = example_study.lcia.result

results["indicator_values"][selected_partitions][("awropo09a", 0)].show_history()
print(results["indicator_values"][selected_partitions][("awropo09a", 0)])

#[selected_partitions][("awropo09a", "00")]