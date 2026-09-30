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


def get_soda4lca_node_datastock(root,
                                export_format="csv",
                                shortname_identifier=None,
                                datastock_uuid=None
                                ):
    """Function that requests the download for a specific datastock of a soda4LCA node specified by the root URL.
    If no datastock_uuid or shortname_identifier is specified (None), the latest available datastock is requested.
    Alternative format for download is "ZIP", which can get pretty large (Epd International ~18GB zip file).
    Note that CSV export is not available for every soda4LCA node.

    The download of larger database exports may take time (EPD Norway for instance can take several minutes to download).
    If one wishes to track the download, the _download_file() function below contains commented out code implementing a
    progress bar for the download using the tqdm library.

    Parameters
    ----------
    root : str
        URL for the soda4LCA API entry point; Including resource, e.g. 'https://oekobaudat.de/OEKOBAU.DAT/resource'
    export_format : str
        Either "csv" (default) or "zip"
    shortname_identifier : str
        Used to select a datastock at the associated endpoint, e.g.
        https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks?format=JSON
        To view available datastocks, give arbitrary string as argument.
    datastock_uuid : str or None
        Alternative identifier to select a datastock for download.
        To view available datastocks, give arbitrary string as argument.
    Returns
    -------
    filepath : Path
        The path to the downloaded database file in the chosen export_format
    """

    root = root
    datastocks_endpoint = root + "/datastocks?format=JSON"

    datastock_dict = _fetch_datastock_metadata(
        datastocks_endpoint,
        datastock_uuid=datastock_uuid,
        shortname_identifier=shortname_identifier
    )
    if not datastock_dict:
        raise ValueError("Error during request of datastock. No datastock was selected.")

    remove_punctuation_map = dict((ord(char), None) for char in '\\/*?:"<>|')
    filename = datastock_dict["shortName"].translate(remove_punctuation_map)

    if export_format=="csv":
        csv_export_endpoint = f"{root}/datastocks/{datastock_dict['uuid']}/exportCSV"
        filepath = _download_file(url=csv_export_endpoint, filename=filename, extension=export_format)
    elif export_format=="zip":
        zip_export_endpoint = f"{root}/datastocks/{datastock_dict['uuid']}/export"
        filepath = _download_file(url=zip_export_endpoint, filename=filename, extension=export_format)
    else:
        raise ValueError(f"Error during request of datastock. Given export format '{export_format}' not supported.")

    print(f"Download successful: '{filepath}'")

    return filepath

def _fetch_datastock_metadata(endpoint, datastock_uuid, shortname_identifier):
    """Requests the latest datastock or the datastock specified by datastock_uuid or the shortname_identifier
    from the associated API endpoint.

    Parameters
    ----------
    endpoint : str
        URL to the API endpoint
    datastock_uuid : str or None
        Used to select the datastock in the list of available datastocks
    shortname_identifier : str or None
        Alternative for selecting a datastock for request

    Returns
    -------
    datastock : Dict or None
        The dictionary element selected from the list of available datastocks
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
        raise KeyError(f"Error during fetch of datastock. Given datastock UUID '{datastock_uuid}' not in"
                       f"available datastocks. Datastocks available: {available_datastocks}")
    elif shortname_identifier:
        for datastock in available_datastocks:
            if shortname_identifier in datastock.get("shortName"):
                return datastock
        raise KeyError(f"Error during fetch of datastock. shortName identifier '{shortname_identifier}' not in "
                       f"available datastocks. Datastocks available: {available_datastocks}")
    else:
        return available_datastocks[-1]

def _download_file(url, filename, extension):
    """Requests and writes datastock to file with the filetype determined by the extension argument.

    Parameters
    ----------
    url : str
        URL to the API endpoint for datastock export
    filename : str
        shortName identifier from the datastock specified in the URL with its UUID
    extension : str
        Either 'csv' or 'zip'

    Returns
    -------
    filepath : Path
        Full path to downloaded file
    """

    remove_punctuation_map = dict((ord(char), None) for char in '\\/*?:"<>|')
    filename = filename.translate(remove_punctuation_map)
    filepath = Path.cwd() / f"{filename}.{extension}"

    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        # from tqdm import tqdm
        #
        # total_size = int(response.headers.get("content-length", 0))
        #
        # with open(filepath, 'wb') as f, tqdm(
        #     desc=filename,
        #     total=total_size,
        #     unit="B",
        #     unit_scale=True,
        #     unit_divisor=1024
        # ) as bar:
        #     for chunk in response.iter_content(chunk_size=1024 * 1024):
        #         if chunk:
        #             f.write(chunk)
        #             bar.update(len(chunk))

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    return filepath
