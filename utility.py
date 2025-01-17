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


def get_latest_oekobaudat_csv():

    root = "https://oekobaudat.de/OEKOBAU.DAT/resource"
    datastocks_endpoint = root + "/datastocks?format=JSON"

    latest_datastock = _fetch_latest_datastock(datastocks_endpoint)
    if not latest_datastock:
        raise ValueError("No available datastocks found")

    datastock_csv_export = _fetch_datastock_csv(root, latest_datastock["uuid"])
    datastock_csv_filepath = _save_csv_file(datastock_csv_export, latest_datastock["name"][0]["value"])

    print(f"Download successful: '{datastock_csv_filepath.name}' saved in project directory.")

    return datastock_csv_filepath

def _fetch_latest_datastock(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        available_datastocks = response.json().get("dataStock", [])
        return available_datastocks[-1] if available_datastocks else None
    except (requests.ConnectionError, requests.HTTPError) as error:
        raise Exception(f"Error fetching datastocks from {endpoint}: {error}")

def _fetch_datastock_csv(root, uuid):
    datastock_csv_export_endpoint = f"{root}/datastocks/{uuid}/exportCSV"
    try:
        response = requests.get(datastock_csv_export_endpoint)
        response.raise_for_status()
        return response.text
    except (requests.ConnectionError, requests.HTTPError) as error:
        raise Exception(f"Error downloading CSV from {datastock_csv_export_endpoint}: {error}")

def _save_csv_file(csv_content, filename):
    filepath = Path.cwd() / f"{filename}.csv"
    with open(filepath, 'w') as f:
        f.write(csv_content)
    return filepath
