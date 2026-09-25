from pigeonpy.data.epddata.source.soda4lcaapi import Soda4LcaApi


class OekobaudatApi(Soda4LcaApi):
    """Class for creating a soda4LCA instance of the Ökobaudat API to load EpdDataset objects.

    Class variables
    ----------
    ROOT : str
        URL for the Oekobaudat API resource point

    Attributes
    ----------
    standards : list
        Supported standards by the tool and available in the Ökobaudat.
    """

    ROOT = "https://oekobaudat.de/OEKOBAU.DAT/resource"

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
            "b2ad66ce-c78d-11e6-9d9d-cec0c932ce01": "wdp",
            # Raw Material Input and Total Material Requirement indicators, not explicitly part of the norm
            # If their use is desired, they need to be added to the indicators JSON file
            "df1d7d28-01b4-45c6-ab35-bde89d3b98f1": "rmi-total",
            "25c2b727-c506-4493-85a8-65eb52593d24": "rmi-biotic-subtotal",
            "03ee44a1-0e8a-471e-a30d-6e779361dddf": "rmi-forestry",
            "505188c3-77bb-4bcd-bb49-2f5f328aa372": "rmi-agriculture",
            "fa8d8e01-cf72-4f7a-b772-71627eb0c481": "tmr-total",
            "fcb01e12-1c4c-4f08-ba2b-4108aed0b85e": "tmr-biotic-subtotal",
            "89c8b6c5-c525-4541-8dbd-211b8db1d3f0": "tmr-forestry",
            "25359720-f52a-4597-980d-3ff571bc2164": "tmr-agriculture",
            "6d1ba770-c0b8-45bb-9d91-44e326359195": "rmi-abiotic-subtotal",
            "1cf37565-0154-4f01-94e4-b4dcbf63b519": "rmi-fossile",
            "755a42f4-bce4-4aaf-af9b-f6ffad4dabb8": "rmi-metals",
            "eb2ad53a-874a-4c97-8017-fa2c06803b9f": "rmi-minerals",
            "25ac461e-57dc-4c53-aeb7-e10e8d077600": "tmr-abiotic-subtotal",
            "32200a68-5488-49d7-9e81-0e93c0f19cc1": "tmr-fossile",
            "4be326ff-416b-400f-b835-472f33b4cf16": "tmr-metals",
            "a9b02237-8034-49ee-850d-876dbe6e148d": "tmr-mineral"
        }
    }

    def __init__(self):
        """Initialize Soda4LcaApi instance with the Ökobaudat API root."""
        super().__init__(self.ROOT)

        self.standards = ["EN15804+A1", "EN15804+A2"]
