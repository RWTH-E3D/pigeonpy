"""Module containing utility functions"""
import requests
from pathlib import Path


def linear_interpolate(dataset1, dataset2, steps, return_datasets=True):
    """This function interpolates linearly between the values of two EPD datasets. One EPD dataset is generated per
    step between dataset1 and dataset2.

    Parameters
    ----------
    dataset1: EpdDataset
        First dataset for interpolation
    dataset2: EpdDataset
        Second dataset for interpolation
    steps: int
        Number of steps that are interpolated
    return_datasets: boolean
        If True, datasets are returned instead of numpy arrays

    Returns
    -------
    interpolated_arrays: list
        Contains the list of interpolated data/ numpy arrays
    """
    array1 = dataset1.data
    array2 = dataset2.data
    interpolation_results = []

    for i in range(1, steps):
        interpolated_array = array1 + i * (array2 - array1) / steps
        if return_datasets:
            interpolated_dataset = type(dataset1)()
            interpolated_dataset.data = interpolated_array
            interpolated_dataset.name = f"_interpolated_dataset_{i}"
            interpolation_results.append(interpolated_dataset)
        else:
            interpolation_results.append(interpolated_array)

    return interpolation_results


def get_latest_oekobaudat_csv(datastock_uuid=None):
    """Function that requests the csv download for a specific datastock of the Oekobaudat database. It fetches the
    available datastocks (different database versions) of the Oekobaudat, chooses either the latest standard/'OBD'
    versionone or the one specified with datastock_uuid, and proceeds to request its CSV file.

    Parameters
    ----------
    datastock_uuid : str or None
        If specified available, it is used to select the datastock to be downloaded.

    Returns
    -------
    datastock_csv_filepath : Path
        The path to the downloaded database in CSV format
    """

    root = "https://oekobaudat.de/OEKOBAU.DAT/resource"
    datastocks_endpoint = root + "/datastocks?format=JSON"

    latest_datastock = _fetch_datastock_metadata(datastocks_endpoint, datastock_uuid=datastock_uuid)
    if not latest_datastock:
        raise ValueError("Error during download of datastock csv. No available datastocks found")

    datastock_csv_export = _fetch_datastock_csv(root, latest_datastock["uuid"])
    datastock_csv_filepath = _save_csv_file(datastock_csv_export, latest_datastock["shortName"])

    print(f"Download successful: '{datastock_csv_filepath.name}' saved in project directory.")

    return datastock_csv_filepath

def _fetch_datastock_metadata(endpoint, datastock_uuid):
    """Requests the latest OBD datastock (if datastock_uuid=None) or the datastock specified by datastock_uuid from the
    associated API endpoint.

    Parameters
    ----------
    endpoint : str
        URL to the API endpoint
    datastock_uuid : str or None
        Used to select the datastock in the list of available datastocks if given.

    Returns
    -------
    datastock : Dict or None
        The dictionary element from the list of available datastocks, which is either the latest datastock with "OBD" in
        its name, the datastock specified by datastock_uuid, or None if the two options before where not successful.
    """
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as error:
        raise Exception(f"Error fetching datastocks from {endpoint}: {error}")

    available_datastocks = response.json().get("dataStock", [])

    if datastock_uuid:
        for datastock in available_datastocks:
            if datastock.get("uuid") == datastock_uuid:
                return datastock

        raise KeyError(f"Error during fetch of oekobaudat csv.\nGiven datastock_uuid '{datastock_uuid}' not in"
                       f"available datastocks.")
    else:
        for datastock in reversed(available_datastocks):
            if "OBD" in datastock.get("shortName"):
                return datastock

    return None

def _fetch_datastock_csv(root, uuid):
    """Requests the datastock identified by the given UUID and returns it as text content.

    Parameters
    ----------
    root : str
        The URL to the CSV export endpoint for a datastock
    uuid : str
        The UUID that indicates the datastock

    Returns
    -------
    response.text : str
        Contains the CSV content
    """
    datastock_csv_export_endpoint = f"{root}/datastocks/{uuid}/exportCSV"
    try:
        response = requests.get(datastock_csv_export_endpoint)
        response.raise_for_status()
        return response.text
    except (requests.ConnectionError, requests.HTTPError) as error:
        raise Exception(f"Error downloading CSV from {datastock_csv_export_endpoint}: {error}")

def _save_csv_file(csv_content, filename):
    """Saves the CSV content to a file in the project directory."""

    remove_punctuation_map = dict((ord(char), None) for char in '\\/*?:"<>|')
    filename = filename.translate(remove_punctuation_map)

    filepath = Path.cwd() / f"{filename}.csv"
    with open(filepath, 'w') as f:
        f.write(csv_content)
    return filepath
