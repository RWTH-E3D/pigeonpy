from data.epddata.source.apiepdsource import ApiEpdSource
import requests
import numpy as np
from io import StringIO
import xml.etree.ElementTree as ET

class OekobaudatAPI(ApiEpdSource):
    """Class that contains methods for fetching datasets in XML format from the oekobaudat API and loading them into
    EpdDataset objects

    Class variables
    ----------
    exchange_uuid_allocations : dict
        A mapping for the exchange flow (pere, perm, etc.) reference UUIDs to the abbreviation of the exchange flow used
        in the environmental indicator json files
    lcia_uuid_allocations : dict
        A mapping for the LCIA result (gwp-total, gwp-fossil, etc.) reference UUIDs to the abbreviation of the indicator
        name used in the environmental indicator json files separated by the associated standard
    not_included_indicators : dict
        A mapping for the environmental indicators of the EN15804+A2 standard which are not calculated in this tool,
        because of the high uncertainties (Ökobaudat Manual)

    Attributes
    ----------
    name : str
        Name given to the EpdSource
    standards : list
        Available standards for this EpdSource
    _root : str
        The root of the oekobaudat API
    _fetched_datasets: dict
        Used to cache already fetched and processed epd data with the associated UUID as key
    _compliance_uuids: dict
        Reference UUIDs for the compliance systems used for the different standards

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
        "b5c602c6-def3-11e6-bf01-fe55135034f3": "pm",
        "b5c632be-def3-11e6-bf01-fe55135034f3": "ir",
        "ee1082d1-b0f7-43ca-a1f0-21e2a4a74511": "etp-fw",
        "2299222a-bbd8-474f-9d4f-4dd1f18aea7c": "htp-c",
        "3af763a5-b7a1-48c9-9cee-1f223481fcef": "htp-nc",
        "b2ad6890-c78d-11e6-9d9d-cec0c932ce01": "sqp"
    }

    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.standards = ["EN15804+A1", "EN15804+A2"]

        self._root = "https://oekobaudat.de/OEKOBAU.DAT/resource"
        self._fetched_datasets = {}  # store already fetched datasets to reduce requests

        self._compliance_uuids = {
            "EN15804+A1": "b00f9ec0-7874-11e3-981f-0800200c9a66",
            "EN15804+A2": [
                "c0016b33-8cf7-415c-ac6e-deba0d21440d",  # Environmental Footprint (EF) 3.0 source dataset
                "d4aa3ec7-b1d7-4a4a-a6cb-37af88dcc902"   # EF 3.1 source dataset
            ]
        }

    def load_epd(self, epd_dataset, epd_id):
        """Method to request epd data based on the given epd_id (UUID), process the returned xml data and populate the
        given epd_dataset instance with the processed epd_data

        Parameters
        ----------
        epd_dataset : EpdDataset
            Instance of either En15804A1Dataset or En15804A2Dataset class
        epd_id : str
            UUID associated to the epd dataset to be loaded

        """

        xml_data = self._single_dataset_request(epd_id)

        process_tree, process_dataset, ns = self._parse_xml(xml_data)

        if not self._check_compliance(process_dataset, ns):
            raise Exception(f"Trying to load a dataset which is not compliant to the defined standard. '{epd_id}'")

        epd_data = {
            **self._extract_indicator_data(
                process_dataset=process_dataset,
                ns=ns,
                xml_base_path=".//default:exchanges/default:exchange",
                uuid_allocations=self.exchange_uuid_allocations
            ),
            **self._extract_indicator_data(
                process_dataset=process_dataset,
                ns=ns,
                xml_base_path=".//default:LCIAResults/default:LCIAResult",
                uuid_allocations=self.lcia_uuid_allocations[epd_dataset.standard]
            )
        }

        self._set_metadata(epd_dataset, epd_id, process_dataset=process_dataset, ns=ns)
        self._populate_data_array(epd_dataset, epd_data)

    def _extract_indicator_data(self, process_dataset, ns, xml_base_path, uuid_allocations):
        """Extracts either the "Exchanges" or "LCIAResults" values for the environmental indicators and their life
        cycle stages out of the xml file

        Parameters
        ----------
        process_dataset : Element
            Root element of the xml tree
        ns : dict
            Namespace dictionary for the xml file
        xml_base_path : str
            Xml path to either the "exchanges" part of the epd (pere, perm, etc.) or to the "LCIAResults" (gwp-total, etc.)
        uuid_allocations : dict
            The allocation needed for the specific call of the method

        Returns
        ----------
        indicator_data : dict
            Contains the environmental indicators as keys for dictionaries which contain the life cycle stages and the
            associated amount as key/ value pairs

        """
        indicator_data = {}
        elements = process_dataset.findall(xml_base_path, ns)

        for element in elements:
            element_uuid = element.find("./default:referenceToFlowDataSet", ns).get("refObjectId") if "exchanges" in xml_base_path \
                else element.find("./default:referenceToLCIAMethodDataSet", ns).get("refObjectId")

            if element.find(".//epd:amount", ns) is None or element_uuid in self.not_included_indicators:
                continue

            element_name = uuid_allocations.get(element_uuid, "unknown indicator")
            if element_name == "unknown indicator":
                allocation = self.lcia_name_allocations.get(element_uuid)
                if allocation:
                    short_description = element.find(".//common:shortDescription[@xml:lang='en']", ns).text
                    element_name = allocation.get(short_description, element_name)

            element_data = indicator_data.setdefault(element_name, {})

            for amount in element.findall(".//epd:amount", ns):
                module = amount.get(f"{{{ns['epd']}}}module").replace("-", "_").lower()  # value of ns['epd'] = http://www.iai.kit.edu/EPD/2013
                if amount.text is not None:
                    element_data[module] = element_data.setdefault(module, float(amount.text or 0.0))  # setdefault() -> Always use first scenrio if multiple exist

            indicator_data.update(element_data)

        return indicator_data

    def load(self, dataset_template):
        """No need to initiate the API connection because only single dataset requests are possible"""
        self.dataset_template = dataset_template()

    def contains_dataset(self, epd_id) -> bool:
        """Only returns True for the check in EpdDatamanager, because there is no other way to check the API
        for available datasets but to make a request. To reduce the number of requests only one is made when actually
        loading the dataset in the _single_dataset_request() method, which handles the case for wrong epd_ids/ UUIDs
        """
        return True

    def _single_dataset_request(self, epd_id):
        """Method to perform a single GET request to the dataset endpoint of the API with a given epd_id/ UUID"""
        try:
            response = requests.get(self._dataset_endpoint(epd_id))
            response.raise_for_status()
            return response.text
        except (requests.ConnectionError, requests.HTTPError) as error:
            raise Exception(f"Error during fetch of dataset with id '{epd_id}': {error}")

    def _dataset_endpoint(self, uuid, response_format="XML"):
        """Creates the URL for the dataset endpoint"""
        return self._root + f"/processes/{uuid}?format={response_format}"

    def _check_compliance(self, dataset, ns) -> bool:
        """Checks the compliance UUIDs in the XML file of the epd for compliance with the defined standard in the class
        instance and the associated compliance UUIDs (see attributes)"""
        compliance_declarations = dataset.findall(".//{*}referenceToComplianceSystem", namespaces=ns)
        for entry in compliance_declarations:
            compliance = entry.get("refObjectId")
            if compliance in self._compliance_uuids[self.dataset_template.standard]:
                return True
        return False

    @staticmethod
    def _set_metadata(epd_dataset, epd_id, process_dataset=None, ns=None, name=None):
        """Sets the metadata attributes in the EpdDataset object either from the XML process_dataset and the associated
        namespaces or from the cached data directly given by the name argument"""
        if process_dataset and ns:
            epd_dataset.name = process_dataset.find(".//default:name/default:baseName", ns).text
        elif name:
            epd_dataset.name = name
        epd_dataset.epd_data_id = epd_id
        # Todo: Implement reference flow value and unit by fetching flow with 'referenceToFlowDataSet' -> 'refObjectId'

    @staticmethod
    def _populate_data_array(epd_dataset, epd_data):
        """Fills the np data array of the epd_dataset instance with the values from the epd_data dictionary

        Parameters
        ----------
        epd_dataset : EpdDataset
            Instance of either En15804A1Dataset or En15804A2Dataset class
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

        a1_a3_index = stage_index_map["a1_a3"]
        if np.count_nonzero(data_array[:, a1_a3_index]) == 0:
            data_array[:, a1_a3_index] = data_array[:, :a1_a3_index].sum(axis=1)

    @staticmethod
    def _parse_xml(xml_data):
        """Method to parse the xml data in string form (as returned from the API request) and create a namespace
        dictionary using the python xml library

        Parameters
        ----------
        xml_data : str
            One string containing the xml file

        Returns
        ----------
        data_set : ElementTree
            Xml Element Tree created by parsing the xml_data
        data_set.getroot() : Element
            The root of the xml element tree
        namespaces : dict
            A namespace dictionary for the xml file
        """
        try:
            data_set = ET.parse(StringIO(xml_data, newline=''))
        except ET.ParseError as error:
            raise ET.ParseError(f"Error while parsing XML data: {error}")

        namespaces = dict([
            node for _, node in ET.iterparse(
                StringIO(xml_data), events = ['start-ns']
            )
        ])
        namespaces.update({
            "xml": "http://www.w3.org/XML/1998/namespace",
            "default": "http://lca.jrc.it/ILCD/Process"
        })

        return data_set, data_set.getroot(), namespaces

    def check_unknown_indicators_in_fetched_datasets(self):
        """
        Only for testing: Check the fetched datasets for any indicators that could not be allocated with the allocations
        present in the indicator allocations (see attributes)
        """
        for loaded_dataset_uuid in self._fetched_datasets:
            if "unknown indicator" in self._fetched_datasets[loaded_dataset_uuid]:
                print(f"Unknown indicator found for dataset with uuid: {loaded_dataset_uuid}")
