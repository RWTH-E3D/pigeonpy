import pandas as pd

from data.epddata.source.apiepdsource import ApiEpdSource
import requests
import numpy as np
from io import StringIO
import xml.etree.ElementTree as ET
from collections import defaultdict


class Soda4LcaApi(ApiEpdSource):
    """Class that contains methods for fetching datasets in XML format from soda4LCA API nodes and loading them into
    EpdDataset objects.

    The class is tested for the Ökobaudat node and the EPD Norway node. Other soda4LCA nodes may be used by passing the
    API root (/resource point) as parameter during instantiation, However, there is no guarantee for successfully loading
    datasets from other nodes.

    Class variables
    ----------
    exchange_uuid_allocations : dict
        A mapping for the exchange flow (pere, perm, etc.) reference UUIDs to the abbreviation of the exchange flow used
        in the environmental indicator JSON files
    lcia_uuid_allocations : dict
        A mapping for the LCIA result (gwp-total, gwp-fossil, etc.) reference UUIDs to the abbreviation of the indicator
        name used in the environmental indicator JSON files separated by the associated standard
    lcia_name_allocations : dict
        For the case that multiple indicators have the same UUID in the XML file, the mapping in this dict uses said
        UUID as identification to then map the indicator names used in the XML file to the indicator abbreviations used
        here
    not_included_indicators : dict
        A mapping for the environmental indicators of the EN15804+A2 standard which are not calculated in this tool,
        because of their high uncertainties (see Ökobaudat Manual)
    compliance_uuids: dict
        Reference UUIDs for the compliance systems used for the different standards

    Attributes
    ----------
    standards : list
        Available standards for this EpdSource
    _root : str
        The root of the API node

    """

    exchange_uuid_allocations = {
        "20f32be5-0398-4288-9b6d-accddd195317": "pere",
        "fb3ec0de-548d-4508-aea5-00b73bf6f702": "perm",
        "53f97275-fa8a-4cdd-9024-65936002acd0": "pert",
        "ac857178-2b45-46ec-892a-a9a4332f0372": "penre",
        "1421caa0-679d-4bf4-b282-0eb850ccae27": "penrm",
        "06159210-646b-4c8d-8583-da9b3b95a6c1": "penrt",
        "c6a1f35f-2d09-4f54-8dfb-97e502e1ce92": "sm",
        "64333088-a55f-4aa2-9a31-c10b07816787": "rsf",
        "89def144-d39a-4287-b86f-efde453ddcb2": "nrsf",
        "3cf952c8-f3a4-461d-8c96-96456ca62246": "fw",
        "430f9e0f-59b2-46a0-8e0d-55e0e84948fc": "hwd",
        "b29ef66b-e286-4afa-949f-62f1a7b4d7fa": "nhwd",
        "3449546e-52ad-4b39-b809-9fb77cea8ff6": "rwd",
        "a2b32f97-3fc7-4af2-b209-525bc6426f33": "cru",
        "d7fe48a5-4103-49c8-9aae-b0b5dfdbd6ae": "mfr",
        "59a9181c-3aaf-46ee-8b13-2b3723b6e447": "mer",
        "4da0c987-2b76-40d6-9e9e-82a017aaaf29": "eee",
        "98daf38a-7a79-46d3-9a37-2b7bd0955810": "eet"
    }

    lcia_uuid_allocations = {
        "ISO21930": {
            "77e416eb-a363-4258-a04e-171d843a6460": "gwp",
            "06dcd26f-025f-401a-a7c1-5e457eb54637": "odp",
            "1e84a202-dae6-42aa-9e9d-71ea48b8be00": "pocp",
            "b4274add-93b7-4905-a5e4-2e878c4e4216": "ap",
            "f58827d0-b407-4ec6-be75-8b69efb98a0f": "ep"
        },
        "EN15804+A1": {
            "77e416eb-a363-4258-a04e-171d843a6460": "gwp",
            "06dcd26f-025f-401a-a7c1-5e457eb54637": "odp",
            "1e84a202-dae6-42aa-9e9d-71ea48b8be00": "pocp",
            "b4274add-93b7-4905-a5e4-2e878c4e4216": "ap",
            "f58827d0-b407-4ec6-be75-8b69efb98a0f": "ep",
            "f7c73bb9-ab1a-4249-9c6d-379a0de6f67e": "adpe",
            "804ebcdf-309d-4098-8ed8-fdaf2f389981": "adpf"
        },
        "EN15804+A2": {
            "6a37f984-a4b3-458a-a20a-64418c145fa2": "gwp-total",
            "5f635281-343e-44fb-83df-1971b155e6b6": "gwp-fossil",
            "2356e1ab-0185-4db5-86e5-16de51c7485c": "gwp-biogen",
            "4331bbdb-978a-490d-8707-eeb047f01a55": "gwp-luluc",
            "a7ea142a-9749-11ed-a8fc-0242ac120002": "gwp-total",
            "a7ea19c0-9749-11ed-a8fc-0242ac120002": "gwp-fossil",
            "a7ea186c-9749-11ed-a8fc-0242ac120002": "gwp-biogen",
            "a7ea1ae2-9749-11ed-a8fc-0242ac120002": "gwp-luluc",
            "b5c629d6-def3-11e6-bf01-fe55135034f3": "odp",
            "b5c611c6-def3-11e6-bf01-fe55135034f3": "ap",
            "b53ec18f-7377-4ad3-86eb-cc3f4f276b2b": "ep-freshwater",
            "b5c619fa-def3-11e6-bf01-fe55135034f3": "ep-marine",
            "b5c614d2-def3-11e6-bf01-fe55135034f3": "ep-terrestrial",
            "b5c610fe-def3-11e6-bf01-fe55135034f3": "pocp",
            "b2ad6494-c78d-11e6-9d9d-cec0c932ce01": "adpe",
            "b2ad6110-c78d-11e6-9d9d-cec0c932ce01": "adpf",
            "b2ad66ce-c78d-11e6-9d9d-cec0c932ce01": "wdp"
        }
    }

    lcia_name_allocations = {
        "a7ea142a-9749-11ed-a8fc-0242ac120002": {
            "Climate change": "gwp-total",
            "Climate change-Fossil": "gwp-fossil",
            "Climate change-Biogenic": "gwp-biogen",
            "Climate change-Land use and land use change": "gwp-luluc"
        }
    }

    # "Additional environmental impact indicators" with high uncertainties (Ökobaudat Manual)
    not_included_indicators = {
        "fb774615-0575-45de-9a89-1ded92f19770": "gwp-iobc/ghg",
        "b5c602c6-def3-11e6-bf01-fe55135034f3": "pm",
        "b5c632be-def3-11e6-bf01-fe55135034f3": "ir",
        "ee1082d1-b0f7-43ca-a1f0-21e2a4a74511": "etp-fw",
        "05316e7a-b254-4bea-9cf0-6bf33eb5c630": "etp-fw",
        "2299222a-bbd8-474f-9d4f-4dd1f18aea7c": "htp-c",
        "3af763a5-b7a1-48c9-9cee-1f223481fcef": "htp-nc",
        "7cfdcfcf-b222-4b26-888a-a55f9fbf7ac8": "htp-nc",
        "b2ad6890-c78d-11e6-9d9d-cec0c932ce01": "sqp"
    }

    module_not_declared_synonyms = ["MND", "ND"]

    compliance_uuids = {
        "ISO21930": "9c1e8451-2321-4498-b459-b6568b6b6547",
        "EN15804+A1": "b00f9ec0-7874-11e3-981f-0800200c9a66",
        "EN15804+A2": [
            "c0016b33-8cf7-415c-ac6e-deba0d21440d",  # Environmental Footprint (EF) 3.0 source dataset
            "d4aa3ec7-b1d7-4a4a-a6cb-37af88dcc902"  # EF 3.1 source dataset
        ]
    }

    def __init__(self, root, *args, **kwargs):
        """Sets the API root according to the passed root argument and sets the available standards for API sources
        available in the tool.

        Parameters
        ----------
        root : str
            Define the root of the soda4LCA API node containing the "/resource" point,
            e.g. https://oekobaudat.de/OEKOBAU.DAT/resource
        """
        super().__init__()
        self._root = root

        self.standards = ["EN15804+A1", "EN15804+A2"]


    def load_epd(self, epd_dataset, epd_id, scenario):
        """Carries out method calls to request epd data based on the given epd_id (UUID); parses the returned
        XML file; extracts indicator data out of the XML file; populates the given epd_dataset instance with the
        extracted indicator data.

        Parameters
        ----------
        epd_dataset : EpdDataset
            Instance of a child class of EpdDataset
        epd_id : str
            UUID for the epd dataset to be loaded
        scenario : str
            Name of the scenario to be used in the dataset if specified
        """

        xml_data = self._single_dataset_request(epd_id)

        process_tree, process_dataset, ns = self._parse_xml(xml_data)

        self._check_compliance(process_dataset, ns, epd_id)

        raw_epd_data = {
            **self._extract_indicator_data(
                process_dataset=process_dataset,
                ns=ns,
                xml_base_path=".//default:exchanges/default:exchange",
                uuid_allocations=self.exchange_uuid_allocations,
                scenario=scenario
            ),
            **self._extract_indicator_data(
                process_dataset=process_dataset,
                ns=ns,
                xml_base_path=".//default:LCIAResults/default:LCIAResult",
                uuid_allocations=self.lcia_uuid_allocations[epd_dataset.standard],
                scenario=scenario
            )
        }

        scenario_resolved_epd_data = self._handle_scenarios(raw_epd_data, scenario, epd_id)

        self._set_metadata(epd_dataset, epd_id, scenario, process_dataset=process_dataset, ns=ns)
        self._populate_data_array(epd_dataset, scenario_resolved_epd_data)

    def _extract_indicator_data(self, process_dataset, ns, xml_base_path, uuid_allocations, scenario):
        """Extracting environmental indicator data out of the fetched dataset XML file by using pythons XML library,
        either for the "Exchanges" (pere, perm, etc.) or for the "LCIAResults" (gwp-total, odp, etc.) part of the
        XML file by distinguishing the two cases based on the given xml_base_path and uuid_allocation.
        The extracted epd data gets checked for any unknown indicators, i.e. a failed allocation of the indicator in the
        XML file to an indicator known to the program.

        Parameters
        ----------
        process_dataset : Element
            Root element of the XML tree
        ns : dict
            Namespace dictionary for the XML file
        xml_base_path : str
            XML path to either the "exchanges" part of the epd or to the "LCIAResults"
        uuid_allocations : dict
            The allocation needed for the specific call of the method

        Returns
        ----------
        raw_indicator_data : DefaultDict
            Contains the indicator values either for the exchanges part or the LCIAResult part of the XML.
            Indicator values are saved with the following nesting:
            raw_indicator_data[<indicator>][<module/life_cycle_stage>][<scenario or None>]
            Additionally, extracted scenario information is included under raw_indicator_data["scenarios"]
        """
        raw_indicator_data = defaultdict(lambda: defaultdict(dict))
        raw_indicator_data["scenarios"] = defaultdict(set)
        scenarios = set([])

        elements = process_dataset.findall(xml_base_path, ns)

        # For verbose info output on failed module loads, uncomment the line below and further
        # lines associated with the variable within this method.
        # invalid_module_definitions = defaultdict(set)
        invalid_module_counter = 0

        for element in elements:
            element_uuid = element.find(
                "./default:referenceToFlowDataSet", ns
            ).get("refObjectId") if "exchanges" in xml_base_path \
                else element.find(
                "./default:referenceToLCIAMethodDataSet", ns
            ).get("refObjectId")

            if element.find(".//epd:amount", ns) is None or element_uuid in self.not_included_indicators:
                continue

            element_name = uuid_allocations.get(element_uuid, "unknown indicator")
            if element_name == "unknown indicator":
                # If no indicator for element_uuid found in uuid_allocations try allocation by unique name
                allocation = self.lcia_name_allocations.get(element_uuid)
                if allocation:
                    short_description = element.find(".//common:shortDescription[@xml:lang='en']", ns).text
                    element_name = allocation.get(short_description, element_name)
                else:
                    dataset_uuid = process_dataset.find(".//common:UUID", ns).text
                    print(f"Unknown indicator found for dataset '{dataset_uuid}: '"
                          f"Unable to allocate indicator uuid '{element_uuid}' to indicator")

            for amount in element.findall(".//epd:amount", ns):
                # value of ns['epd'] = http://www.iai.kit.edu/EPD/2013
                module = amount.get(f"{{{ns['epd']}}}module").replace("-", "_").lower()
                scenario = amount.get(f"{{{ns['epd']}}}scenario") # None if missing

                if amount.text is not None and amount.text not in self.module_not_declared_synonyms:
                    try:
                        value = float(amount.text or 0.0)
                    except (TypeError, ValueError):
                        invalid_module_counter += 1
                        # invalid_module_definitions[element_name].add((module, amount.text))
                        value = 0.0

                    raw_indicator_data[element_name][module][scenario] = value # E.g. element_name=pere, module=a1_a3, scenario=None

                    if scenario:
                        scenarios.add(scenario)
                        raw_indicator_data["scenarios"]["scenarios_unique"] = scenarios
                        raw_indicator_data["scenarios"][module].add(scenario)

        if invalid_module_counter > 0:
            section = xml_base_path.split("/")[2].split(":")[1]
            print(f"Warning: {invalid_module_counter} module values for '{section}' in dataset "
                  f"'{process_dataset.find('.//common:UUID', ns).text}' could not be converted to float and were "
                  f"replaced with 0.0")
            # for indicator, invalid_entries in invalid_module_definitions.items():
            #     formatted = ", ".join(
            #         f"{module} '{value}'" for module, value in sorted(invalid_entries)
            #     )
            #     print(f"  {indicator}: {formatted}")

        return raw_indicator_data

    @staticmethod
    def _handle_scenarios(raw_epd_data, scenario, epd_id):
        """Resolves scenario dependent EPD data.

        Extracts available scenarios from the dictionary containing the raw EPD data, indicated by duplicate module
        (life cycle stage) entries. If scenarios are present, only the module entries corresponding to the indicated
        scenario are kept. When the scenario parameter is equal to "use_first", the first scenario is used. This is
        intended for testing the loading of datasets. When a given scenario is not found within the available scenarios
        or no scenario is given in the case of a dataset containing scenarios, an Exception is raised. The Exception
        prints out the associated epd_id and the available scenarios.

        Parameters
        ----------
        raw_epd_data : DefaultDict
            If a dataset contains scenarios, this dictionary holds multiple values for the scenario modules
        scenario : str
            Name of the scenario to use or None
        epd_id : str
            UUID used to create the lca_dataset_bind and given to this method for clarity in case an error is raised

        Returns
        -------
        resolved_epd_data : Dict
            Contains no duplicate value entries for modules, only the values of the selected scenarios, if scenarios exist

        Raises
        ------
        Exception :
            When an EPD dataset contains scenarios, but none is given, or the given scenario is not present in the
            available scenarios.
        """
        if pd.isna(scenario):
            scenario = None
        else:
            scenario = str(scenario)

        resolved_epd_data = {}
        all_scenarios_module_resolved = None
        all_scenarios_unique = None

        if len(raw_epd_data["scenarios"]) > 0:
            all_scenarios_module_resolved = raw_epd_data.pop("scenarios")
            all_scenarios_unique = all_scenarios_module_resolved.pop("scenarios_unique")

        for indicator, modules in raw_epd_data.items():
            resolved_epd_data[indicator] = {}

            for module, indicator_values in modules.items():

                # "use_first" for testing if datasets can be loaded with test_load_dataset_methods.py, uses first scenario
                if scenario == "use_first":
                    resolved_epd_data[indicator][module] = next(iter(indicator_values.values()))
                    continue

                # No scenarios, only 1 value for the module
                if len(indicator_values) == 1:
                    resolved_epd_data[indicator][module] = next(iter(indicator_values.values()))
                    continue

                # Scenarios present, but nothing specified by user
                if pd.isna(scenario) or scenario is None:
                    pretty_scenarios = {
                        module: sorted(scenarios)
                        for module, scenarios in all_scenarios_module_resolved.items()
                    }
                    raise Exception(
                        f"Error during loading of dataset. Dataset with id '{epd_id}' contains scenarios. Please specify one.\n"
                        f"Available scenarios:\n "
                        f"{pretty_scenarios}"
                    )

                # Scenarios present and user specified a scenario, but it is not in the available scenarios
                if scenario not in all_scenarios_unique:
                    pretty_scenarios = {
                        module: sorted(scenarios)
                        for module, scenarios in all_scenarios_module_resolved.items()
                    }
                    raise Exception(
                        f"KeyError during loading of dataset with id '{epd_id}'. "
                        f"Given scenario '{scenario}' does not match with available scenarios for module '{module}'. "
                        f"Available scenarios: {pretty_scenarios}"
                    )

                # Specified scenario by user only present in another module -> skips current module and continues
                if scenario in all_scenarios_unique and scenario not in indicator_values:
                    continue

                resolved_epd_data[indicator][module] = indicator_values[scenario]

        return resolved_epd_data

    def load(self, dataset_template):
        """Checks the LCIA UUID allocations by requesting the LCIA methods, i.e. indicators, used in the latest datastock
        and prints out unidentified indicators. Datastocks are different versions of the database. No additional need to
        initiate an API connection because only single dataset requests are possible. Also sets the dataset template as
        attribute. Method is called when a Soda4LcaApi source is registered in the EpdDataManager.

        Parameters
        ----------
        dataset_template : EpdDataset
            Indicates the standard used for the instance.
        """
        self.dataset_template = dataset_template

        latest_datastock_uuid = self._uuid_from_latest_datastock()

        lcia_methods_xml_data = self._make_request(self._root + f"/datastocks/{latest_datastock_uuid}/lciamethods").text
        process_tree, process_dataset, ns = self._parse_xml(lcia_methods_xml_data)

        for lcia_method in process_dataset.findall(".//l:LCIAMethod", ns):
            uuid = lcia_method.find(".//sapi:uuid", ns).text
            if (uuid in self.lcia_uuid_allocations[self.standards[0]]) or (
                    uuid in self.lcia_uuid_allocations[self.standards[1]]) or (uuid in self.not_included_indicators):
                continue
            else:
                lcia_method_name = lcia_method.find(".//sapi:name[@xml:lang='en']", ns).text
                print(f"Unknown indicator found: '{uuid}', '{lcia_method_name}'")

    def contains_dataset(self, epd_id) -> NotImplementedError:
        """Raises a NotImplementedError, when called from within EpdDataManager, which is then handled in the
        EpdDataManager. The EpdDataManager then proceeds to the load_epd method for the Soda4LcaApi instance because,
        which in turn raises an Error, if the dataset is not present. There is no other way to check the API for
        available datasets but to make a request. The soda4LCA API does not allow searching for a dataset by UUID.
        To reduce the number of requests only one is made to load the dataset in the _single_dataset_request() method,
        which handles the case for wrong epd_ids/ UUIDs. Not optimal.
        """
        raise NotImplementedError

    def _uuid_from_latest_datastock(self):
        """Perform API request to the datastocks endpoint and return the UUID of the latest datastock. The UUID is
        needed for another request to verify the LCIA method UUID allocations (uuid_allocations)."""
        available_datastocks = self._make_request(self._root + "/datastocks?format=JSON")
        # request returns dictionary with list of dictionaries as only entry with the key 'dataStock'
        uuid_from_latest_datastock = available_datastocks.json().get(
            'dataStock',
            list(available_datastocks.json().values())[0]
        )[-1].get("uuid")
        return uuid_from_latest_datastock

    def _single_dataset_request(self, uuid, response_format="XML"):
        """Calls method to perform API request with the URL for the dataset endpoint of the API. Returns the text content
        of the response containing the XML file as plain text."""
        response = self._make_request(self._root + f"/processes/{uuid}?format={response_format}")
        if response.status_code != 200:
            raise Exception(f"Request of dataset with uuid '{uuid}' not successful. {response.text}")
        return response.text

    def _check_compliance(self, dataset, ns, epd_id):
        """Checks the compliance UUIDs in the XML file of the epd for compliance with the defined standard in the class
        instance and the associated compliance UUIDs (see class variables).

        Parameters
        ----------
        dataset : ElementTree
            parsed XML content of the dataset
        ns : Dict
            Namespace dictionary for the XML
        epd_id : str
            UUID used to indicate the dataset, if no compliance can be found.

        Raises
        ------
        Exception :
            For the case, no compliance between dataset and used standard within the class instance could be found.
        """
        compliance_declarations = dataset.findall(".//{*}referenceToComplianceSystem", namespaces=ns)
        dataset_compliance_systems = []
        for entry in compliance_declarations:
            compliance = entry.get("refObjectId")
            if compliance in self.compliance_uuids[self.dataset_template.standard]:
                return
            else:
                dataset_compliance_systems.append(compliance)

        raise Exception(f"Error trying to load dataset with id '{epd_id}'.\n Dataset compliance system(s) "
                        f"'{dataset_compliance_systems}' not compliant to the defined standard.")

    @staticmethod
    def _make_request(request_url):
        """Method to perform a single http request to the API endpoint given in the request url. If the resource is not
        available, either an HTTP 404 error is raised or a concrete output is given, depending on the node."""
        try:
            response = requests.get(request_url)
            response.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError) as error:
            raise Exception(f"Error during http request: {error}")
        return response

    @staticmethod
    def _set_metadata(epd_dataset, epd_id, scenario, process_dataset=None, ns=None, name=None):
        """Sets metadata attributes in the EpdDataset object either from the XML process_dataset and the associated
        namespaces or from the cached data directly given by the name argument."""
        if (process_dataset is not None) and (ns is not None):
            epd_dataset.name = process_dataset.find(".//default:name/default:baseName", ns).text
        elif name:
            epd_dataset.name = name
        epd_dataset.epd_data_id = epd_id
        epd_dataset.scenario = scenario

    @staticmethod
    def _populate_data_array(epd_dataset, epd_data):
        """Fills the np data array of the epd_dataset instance with the values from the epd_data dictionary.

        Uses the environmental_indicators and life_cycle_stages lists available as class variables in the EpdDataset
        instance to extract the indicator values from the given epd_data dictionary and assign them to the correct row
        and column indices.
        When the a1_a3 stage is not defined, i.e. zero, the sum of a1, a2, and a3 is assigned to it.

        Parameters
        ----------
        epd_dataset : EpdDataset
            Instance of EpdDataset class
        epd_data : dict
            Contains the environmental indicators as keys for dictionaries which contain the life cycle stages and the
            associated amount as key/ value pairs

        """
        data_array = epd_dataset.data
        stage_index_map = {stage.abbreviation: index for index, stage in enumerate(epd_dataset.life_cycle_stages)}

        for row_index, indicator in enumerate(epd_dataset.environmental_indicators):
            indicator_data = epd_data.get(indicator.abbreviation, {})

            for stage, value in indicator_data.items():
                if stage in stage_index_map:
                    data_array[row_index, stage_index_map[stage]] = value

        if "a1_a3" in epd_dataset.life_cycle_stages:
            a1_a3_index = stage_index_map["a1_a3"]
            if np.count_nonzero(data_array[:, a1_a3_index]) == 0:
                data_array[:, a1_a3_index] = data_array[:, :a1_a3_index].sum(axis=1)

    @staticmethod
    def _parse_xml(xml_data):
        """Method to parse the XML data in string form (as returned from the API request) and create a namespace
        dictionary using the python XML library.

        Parameters
        ----------
        xml_data : str
            One string containing the XML file

        Returns
        ----------
        data_set : ElementTree
            XML Element Tree created by parsing the given xml_data
        data_set.getroot() : Element
            The root of the XML element tree
        namespaces : dict
            A namespace dictionary for the XML file
        """
        try:
            data_set = ET.parse(StringIO(xml_data, newline=''))
        except ET.ParseError as error:
            raise ET.ParseError(f"Error while parsing XML data: {error}")

        namespaces = dict(
            node for _, node in ET.iterparse(
                StringIO(xml_data), events = ['start-ns']
            )
        )
        namespaces.update({
            "xml": "http://www.w3.org/XML/1998/namespace",
            "default": "http://lca.jrc.it/ILCD/Process"
        })

        return data_set, data_set.getroot(), namespaces
