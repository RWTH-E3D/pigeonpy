from pathlib import Path
import json
from logic.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage import LifeCycleStage

class EpdAttributeLoader:
    def __init__(self):
        self.indicators_a1_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "indicators_en_15804_a1.json"
        self.indicators_a2_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "indicators_en_15804_a2.json"
        self.life_cycle_stages_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "life_cycle_stages_en_15978.json"

        self.indicators_a1 = []
        self.indicators_a2 = []
        self.indicators_a1_dimensionless = []
        self.indicators_a2_dimensionless = []
        self.life_cycle_stages = []
        self._load_indicators()
        self._load_stages()

    def _load_indicators(self):
        with open(self.indicators_a1_path) as a1, open(self.indicators_a2_path) as a2:
            a1_data = json.load(a1)['indicators_en_15804_a1']
            a2_data = json.load(a2)['indicators_en_15804_a2']

            def process_indicators(data, indicators_list, dimensionless_list):
                for indicator in data:
                    indicators_list.append(EnvironmentalIndicator(**indicator))
                    dimensionless_list.append(EnvironmentalIndicator(
                        abbreviation=indicator["abbreviation"],
                        name=indicator["name"],
                        unit="-",
                        description=indicator["description"]
                    ))

            process_indicators(a1_data, self.indicators_a1, self.indicators_a1_dimensionless)
            process_indicators(a2_data, self.indicators_a2, self.indicators_a2_dimensionless)

    def _load_stages(self):
        with open(self.life_cycle_stages_path) as lcs:
            lcs_data = json.load(lcs)['LifeCycleStages']
            self.life_cycle_stages = [LifeCycleStage(**stage) for stage in lcs_data]
