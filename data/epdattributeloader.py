from pathlib import Path
import json
from epd.environmentalindicator import EnvironmentalIndicator
from epd.lifecyclestage import LifeCycleStage

class EpdAttributeLoader:
    """Handles the loading of environmental indicators and life cycle stages from the json files into lists containing
    EnvironmentalIndicator and LifeCycleStages instances. It is also responsible for handling the customization of
    attributes.

    Every EpdDataset class holds one EpdAttributeLoader instance that is responsible for assigning the environmental
    indicators and life cycle stages to the EpdDataset class and subclasses associated class variables. For the case of
    custom attributes the EpdAttributeLoader of the class is exchanged with a new EpdAttributeLoader containing the
    wished attributes (see study class).

    Attributes
    ----------
    indicators_a1_path : str
        Path to the environmental indicator json for the EN15804+A1 standard
    indicators_a2_path : str
        Path to the environmental indicator json for the EN15804+A2 standard
    life_cycle_stages_path : str
        Path to the life cycle stages json according to the EN15804 standard
    environmental_indicators_to_be_used : list
        If it is specified and not None, it contains the environmental indicator abbreviations that are defined for the
        study. It defaults to None, i.e. all environmental indicators from the standard/ json file are used.
    life_cycle_stages_to_be_used : list
        If it is specified and not None, it contains the life cycle stage abbreviations that are defined for the
        study. It defaults to None, i.e. all life cycle stages from the standard/ json file are used.
    dataset_template : EpdDataset
        Not an instance of EpdDataset but the EpdDataset class itself (typically a subclass of EpdDataset used to
        indicate the standard for a study).
    indicators_a1 : list
        Contains the EnvironmentalIndicator objects for all available indicators of the EN15804+A1 standard in the json
        file. Gets assigned when an instance is created.
    indicators_a2 : list
        Contains the EnvironmentalIndicator objects for all available indicators of the EN15804+A2 standard in the json
        file. Gets assigned when an instance is created.
    life_cycle_stages : list
        Contains the LifeCycleStage objects for all available indicators of the EN15804 standard in the json file. Gets
        assigned when an instance is created.

    """

    def __init__(self,
                 environmental_indicators: list = None,
                 life_cycle_stages: list = None,
                 dataset_template = None
                 ):
        """First sets the paths to the JSON files containing the indicators and life cycle stages available in the tool.
        Then, the content of the JSON files is loaded into the associated lists for indicators_a1, indicators_a2, and
        life_cycle_stages by calling the _load_indicators() and _load_stages() functions.
        When environmental_indicators and/or life_cycle_stages arguments are specified, i.e. not all are used, the lists
        for indicators and stages of the dataset_template are modified accordingly.

        Parameters
        ----------
        environmental_indicators : list
            If it is specified and not None, it contains the environmental indicator abbreviations that are defined for the
            study. It defaults to None, i.e. all environmental indicators from the standard/ JSON file are used.
        life_cycle_stages : list
            If it is specified and not None, it contains the life cycle stage abbreviations that are defined for the
            study. It defaults to None, i.e. all life cycle stages from the standard/ JSON file are used.
        dataset_template : EpdDataset
            Not an instance of EpdDataset but the EpdDataset class itself (typically a subclass of EpdDataset to indicate
            the standard). If it is specified (together with environmental_indicators and life_cycle_stages), it is used to
            customize the indicators and life cycle stages for the dataset_template (changes are present in the whole study
            instance/ scope) based on the given environmental_indicators and life_cycle_stages.
        """
        self.indicators_a1_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "indicators_en_15804_a1.json"
        self.indicators_a2_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "indicators_en_15804_a2.json"
        self.indicators_iso_21930_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "indicators_iso_21930.json"
        self.life_cycle_stages_path = Path(__file__).parent.parent / "data" / "input" / "inputdata" / "life_cycle_stages_en_15978.json"
        self.environmental_indicators_to_be_used = environmental_indicators
        self.life_cycle_stages_to_be_used = life_cycle_stages
        self.dataset_template = dataset_template

        self.indicators_a1 = []
        self.indicators_a2 = []
        self.indicators_iso_21930 = []
        self.life_cycle_stages = []

        self._load_indicators()
        self._load_stages()

        if self.environmental_indicators_to_be_used and self.dataset_template:
            self.dataset_template.environmental_indicators = self._filter_attributes(
                self.environmental_indicators_to_be_used,
                self.dataset_template.environmental_indicators
            )
        if self.life_cycle_stages_to_be_used and self.dataset_template:
            self.dataset_template.life_cycle_stages = self._filter_attributes(
                self.life_cycle_stages_to_be_used,
                self.dataset_template.life_cycle_stages
            )

    def _load_indicators(self):
        """Opens the JSON files containing environmental indicators and loads the data into EnvironmentalIndicator
        objects which are then appended to the associated list."""
        with (open(self.indicators_a1_path) as a1,
              open(self.indicators_a2_path) as a2,
              open(self.indicators_iso_21930_path) as iso_21930):

            a1_data = json.load(a1)['indicators_en_15804_a1']
            a2_data = json.load(a2)['indicators_en_15804_a2']
            iso_21930_data = json.load(iso_21930)['indicators_iso_21930']

            def process_indicators(data, indicators_list):
                for indicator in data:
                    indicators_list.append(EnvironmentalIndicator(**indicator))

            process_indicators(a1_data, self.indicators_a1)
            process_indicators(a2_data, self.indicators_a2)
            process_indicators(iso_21930_data, self.indicators_iso_21930)

    def _load_stages(self):
        """Opens the JSON file containing the life cycle stages and loads the data into LifeCycleStage objects which
        are then appended to the associated list."""
        with open(self.life_cycle_stages_path) as lcs:
            lcs_data = json.load(lcs)['LifeCycleStages']
            self.life_cycle_stages = [LifeCycleStage(**stage) for stage in lcs_data]

    @staticmethod
    def _filter_attributes(attributes_to_be_used, attributes_to_be_filtered):
        """Takes the existing list of attributes (environmental indicators or life cycle stages) and creates a new list
        containing only the objects of the attributes given by the attribute abbreviations in the attributes_to_be_used
        parameter.

        Parameters
        ----------
        attributes_to_be_used : list
            Contains the wished attributes as a list of abbreviations
        attributes_to_be_filtered : list
            Contains the current attributes (complete list of attributes).

        Returns
        -------
        filtered_attributes : list
            Contains the objects of the attributes for all attribute abbreviations given with the attributes_to_be_used
            list.
        """
        filtered_attributes = [
            attribute for attribute in attributes_to_be_filtered
            if attribute.abbreviation in attributes_to_be_used
        ]
        return filtered_attributes
