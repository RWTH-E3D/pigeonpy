import pandas as pd
import json
import uuid
from pathlib import Path


def export(data,
           path=None,
           file_format="csv",
           drop_rows=False,
           add_uuid=False):

    """Function to export EPD data either to CSV or JSON.

    Handles both single datasets and pd.Series objects as present in the calculation results in study.result for
    instance. In the case of single dataset export (data argument is an EpdDataset object), the EPD is first converted
    into a dictionary to allow same handling as for multiple datasets. Available export formats are CSV and teco_json.
    When using the CSV format, the two arguments drop_rows and add_uuid may be used.

    Parameters
    ----------
    data : EpdDataset or pd.Series
        Data for export
    path : Path or str
        If no path is given, data is exported into data/output/outputdata/
    file_format : str
        Export format, 'csv' or 'teco_json' (JSON) available
    drop_rows : bool
        Removes rows (row = life cycle stage), where all indicator values are zero.
    add_uuid : bool
        Creates and adds a UUID to each exported dataset (teco_json export assigns UUIDs to each dataset anyway).
    """

    # If data is single dataset -> convert into dict object for same handling
    if hasattr(data, "items"):
        datasets = data
        path = _resolve_path(path, file_format)
    else:
        datasets = {data.name: data}
        path = _resolve_path(path, file_format, default_name=data.name)

    if file_format == "csv":
        _export_to_csv(datasets, path, drop_rows, add_uuid)
    elif file_format == "teco_json":
        _export_to_json(datasets, path)
    else:
        raise ValueError(f"Unsupported format: {file_format}")

    print(f"Exported data to: {path}")

def export_study_result(study_name,
                        result_dict,
                        output_dir=None,
                        file_format="csv",
                        drop_rows=False,
                        add_uuid=False,
                        merge=True):

    """Function to export study results either to a CSV or a JSON file.

    If merge=True, this function combines all result dictionaries present in study.result into one dictionary to
    export one file for the whole result. If merge=False, all results are stored separately with the following nameing
    convention:
    <result_name e.g. indicator_value>_<result_partition>.<file_format>

    study_name : str
        Defined name of the study to export
    result_dict: Dict
        Result dictionaries present in the result attribute in the Study class.
    output_dir: Path or str
        Path to the output directory (not file). If None, output in data/output/outputdata/
    file_format : str
        Export format, 'csv' or 'teco_json' (JSON) available
    drop_rows : bool
        Removes rows (row = life cycle stage), where all indicator values are zero.
    add_uuid : bool
        Creates and adds a UUID to each exported dataset
    merge : bool
        If True, all dictionaries/results are combined and exported as one dictionary/result
    """
    # Export everything into one file
    if merge:
        datasets = _combine_all_datasets_into_one_dictionary(result_dict)

        if output_dir:
            output_path = Path(output_dir) / f"{study_name}_export.{file_format}"
        else:
            output_path = Path(__file__).parent.parent.parent / "data" / "output" / "outputdata" / f"{study_name}_export.{file_format}"

        export(
            datasets,
            path=output_path,
            file_format=file_format,
            drop_rows=drop_rows,
            add_uuid=add_uuid
        )
    # Export each result type and partition into an individual file
    else:
        for result_name, result_partitions in result_dict.items():
            for result_partition, result_object in result_partitions.items():

                if output_dir:
                    output_path = Path(output_dir) / f"{result_name}_{result_partition}.{file_format}"
                else:
                    output_path = Path(__file__).parent.parent.parent / "data" / "output" / "outputdata" / f"{result_name}_{result_partition}.{file_format}"

                export(
                    result_object,
                    path=output_path,
                    file_format=file_format,
                    drop_rows=drop_rows,
                    add_uuid=add_uuid
                )


def _export_to_csv(datasets, path, drop_rows, add_uuid):
    """Exports dataset(s) in datasets argument to CSV file.

    Creates a list of dataframes similar to soda4LCA datastock CSV exports using the _dataset_to_dataframe function.
    Then uses concat to combine them and the resulting dataframe is written to a CSV file at the given path."""
    frames = [
        _dataset_to_dataframe(name, ds, drop_rows, add_uuid)
        for name, ds in datasets.items()
    ]

    pd.concat(frames, ignore_index=True).to_csv(path, sep=";", index=False)

def _export_to_json(datasets, path):
    """Exports dataset(s) in datasets argument to teco_json (JSON) file.

    Creates a dictionary containing every dataset in datasets using the _dataset_to_json_dict function and dumps it into
    a JSON file at the given path."""
    export_dict = {}

    for name, ds in datasets.items():
        export_dict.update(_dataset_to_json_dict(name, ds))

    with open(path, "w") as f:
        json.dump(export_dict, f, indent=4)

def _dataset_to_dataframe(name, dataset, drop_rows, add_uuid):
    """Used for CSV export. Creates a pd.Dataframe object for the given dataset with a structure similar to soda4LCA
    datastock CSV exports.

    Parameters
    ----------
    name : str
        Dataset name used in the export
    dataset : EpdDataset
        Contains the data to be transformed into a pandas Dataframe
    drop_rows : bool
        If True, removes rows (row = life cycle stage), where all indicator values are zero.
    add_uuid : bool
        If True, adds a UUID column and creates a UUID for each exported dataset.
    """
    df = pd.DataFrame(
        data=dataset.data.transpose(),
        columns=[indicator.abbreviation for indicator in dataset.environmental_indicators]
    )

    df.insert(0, "Module", value=pd.Series([stage.abbreviation for stage in dataset.life_cycle_stages]))
    df.insert(0, "Compliance", _get_compliance(dataset))
    df.insert(0, "Name (en)", str(name))

    if add_uuid:
        df.insert(0, "UUID", str(uuid.uuid4()))

    if drop_rows:
        start_idx = df.columns.get_loc("Module") + 1
        df = df[~df.iloc[:, start_idx:].eq(0).all(axis=1)]

    return df

def _dataset_to_json_dict(name, dataset):
    """Creates dictionaries with teco_json structure to dump into JSON file.

    Parameters
    ----------
    name : str
        Dataset name used in the export.
    dataset : EpdDataset
        Contains the data to be transformed into a dictionary with teco_json structure.
    """
    uid = str(uuid.uuid4())

    result = {
        uid: {
            "name": str(name),
            "ref_flow": {"value": "", "unit": ""}
        }
    }

    for i, indicator in enumerate(dataset.environmental_indicators):
        result[uid][indicator.abbreviation] = {"unit": indicator.unit}

        for j, stage in enumerate(dataset.life_cycle_stages):
            value = dataset.data[i][j]
            if value != 0.0:
                result[uid][indicator.abbreviation][stage.abbreviation] = value

    return result


def _combine_all_datasets_into_one_dictionary(result):
    """Helper function for combining all results in the result attribute of the Study class into one dictionary. Takes
    the result dictionary from the Study class as input and returns one dictionary containing the content of the result
    dictionary.

    Parameters
    ----------
    result : dict
        result attribute of the Study class type parent dictionary containing sub dictionaries for the calculated
        partitions, which in turn contain the EpdDataset objects.

    Returns
    -------
    all_datasets : dict
        One large dictionary containing all dictionaries from the result dictionary on one dictionary level.
    """
    all_datasets = {}

    for result_name, result_partitions in result.items():
        for result_partition, result_object in result_partitions.items():

            prefix = f"{result_name}_{result_partition}"

            # Multiple datasets (dict-like/Series)
            if hasattr(result_object, "items"):
                for name, ds in result_object.items():
                    all_datasets[f"{prefix}_{name}"] = ds
            # Single dataset
            else:
                all_datasets[prefix] = result_object

    return all_datasets

def _resolve_path(path, file_format, default_name="lca_data_export"):
    """Helper function to create a path, if None is given to export function. Path creation either uses the default_name
    'lca_data_export' for filename (export of Series/multiple datasets into one file) or uses the name given with
    default_name, which equals to the dataset name (export of single dataset)."""
    if path:
        return Path(path)

    extension = "json" if file_format == "teco_json" else "csv"
    filename = f"{default_name}.{extension}"

    return Path(__file__).parent / "outputdata" / filename

def _get_compliance(dataset):
    """Helper function to reduce redundancy."""
    return "'EN 15804'" if dataset.standard == "EN15804+A1" else "'EN 15804+A2'"
