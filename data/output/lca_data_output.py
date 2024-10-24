import pandas as pd
import json
import uuid
import os


def export_calculated_dataframe(df, path="lca_data_export.csv", file_format="csv", drop_rows=False, add_uuid=False):
    """Function to handle the given/ not given path and call the correct function depending on file_format

    Parameters
    ----------
    df : pd Dataframe
        Pandas dataframe containing calculation results
    path : str
        Path to location where exported file is created containing filename
    file_format: str
        String containing the file format the calculation results are exported to
    drop_rows: Boolean
        If True, rows/ life_cycle_stages of a dataset that are empty (all equal to 0) are dropped in the export dataframe
    add_uuid: Boolean
        If True, adds an uuid column to the exported csv file
    """

    dir_path = os.path.dirname(__file__)
    if file_format == "teco_json":
        if path == "lca_data_export.csv":
            export_dataframe_to_teco_json(df=df, path=os.path.join(dir_path, "lca_data_export.json"))
        else:
            export_dataframe_to_csv(df=df, path=path)
    else:
        if path == "lca_data_export.csv":
            export_dataframe_to_csv(df=df, path=os.path.join(dir_path, path), drop_rows=drop_rows, add_uuid=add_uuid)
        else:
            export_dataframe_to_csv(df=df, path=path, drop_rows=drop_rows, add_uuid=add_uuid)


def export_dataframe_to_csv(df, path, drop_rows=False, add_uuid=False):
    """Function that exports the given dataframe with calculation results to a csv file in the location given by path

    Parameters
    ----------
    df : pd Dataframe
        Pandas dataframe containing calculation results
    path : str
        Path to location where exported file is created containing filename
    drop_rows: Boolean
        If True, rows/ life_cycle_stages of a dataset that are empty (all equal to 0) are dropped in the export dataframe
    add_uuid: Boolean
        If True, adds an uuid column to the exported csv file
    """

    export_dataframe = pd.DataFrame()

    for index, row in df.items():
        dataset = row
        temp_df = pd.DataFrame(data=dataset._data.transpose(),
                               index=[x for x in range(len(dataset.life_cycle_stages))],
                               columns=[indicator.abbreviation for indicator in dataset.environmental_indicators])

        temp_df.insert(0, "Modul", value=pd.Series([stage.abbreviation for stage in dataset.life_cycle_stages]))
        if dataset.standard == "EN15804+A1":
            temp_df.insert(0, "Konformität", value="'EN 15804'")
        else:
            temp_df.insert(0, "Konformität", value="'EN 15804+A2'")
        temp_df.insert(0, "Name (de)", value=str(index))

        if add_uuid:
            temp_df.insert(0, "UUID", value=str(uuid.uuid1()))

        # drop rows/ life cycle stages where all values are equal to zero
        help_column_index = temp_df.columns.get_loc('pere')
        if drop_rows:
            temp_df = temp_df[~temp_df.iloc[:, help_column_index:].isin([0]).all(axis=1)]

        export_dataframe = pd.concat([export_dataframe, temp_df], ignore_index=True)

    export_dataframe.to_csv(path, sep=';', index=False)


def export_dataframe_to_teco_json(df, path):
    """Function that exports the given dataframe with calculation results to a json file formatted according to the
     teco_json format in the location given by path

    Parameters
    ----------
    df : pd Dataframe
        Pandas dataframe containing calculation results
    path : str
        Path to location where exported file is created containing filename
    """

    export_dict = {}
    for index, row in df.items():
        dataset = row
        temp_uuid = str(uuid.uuid1())
        # add ref_flow attributes here when meta-data is passed by dunder methods in EpdDataset
        temp_dict = {temp_uuid: {'name': str(index),
                                 'ref_flow': {
                                     'value': '',
                                     'unit': ''
                                 }}}

        for indicator_index, indicator in enumerate(dataset.environmental_indicators):
            temp_dict[temp_uuid][indicator.abbreviation] = {'unit': indicator.unit}
            for stage_index, stage in enumerate(dataset.life_cycle_stages):
                if dataset._data[indicator_index][stage_index] != 0.0:
                    temp_dict[temp_uuid][indicator.abbreviation][stage.abbreviation] = dataset._data[indicator_index][
                        stage_index]

        export_dict.update(temp_dict)

    with open(path, 'w') as f:
        json.dump(export_dict, f, indent=4, separators=(',', ': '))


def export_single_dataset_to_csv(dataset, path, drop_rows=False, add_uuid=False):
    """Function that exports the data matrix of a single dataset to a csv file in the location given by path

    Parameters
    ----------
    dataset : EpdDataset
        Instance of EpdDataset
    path : str
        Path to location where exported file is created containing filename
    drop_rows: Boolean
        If True, rows/ life_cycle_stages of the dataset that are empty (all equal to 0) are dropped in the export dataframe
    add_uuid: Boolean
        If True, adds an uuid column to the exported csv file
    """

    if path is None:
        path = os.path.join(os.path.dirname(__file__), (dataset._name + ".csv"))

    export_df = pd.DataFrame(data=dataset._data.transpose(),
                             index=[x for x in range(len(dataset.life_cycle_stages))],
                             columns=[indicator.abbreviation for indicator in dataset.environmental_indicators])
    export_df.insert(0, "Modul", value=pd.Series([stage.abbreviation for stage in dataset.life_cycle_stages]))
    if dataset.standard == "EN15804+A1":
        export_df.insert(0, "Konformität", value="'EN 15804'")
    else:
        export_df.insert(0, "Konformität", value="'EN 15804+A2'")
    export_df.insert(0, "Name (de)", value=str(dataset._name))
    if add_uuid:
        export_df.insert(0, "UUID", value=str(uuid.uuid1()))
    # drop rows/ life cycle stages where all values are equal to zero
    help_column_index = export_df.columns.get_loc('pere')
    if drop_rows:
        export_df = export_df[~export_df.iloc[:, help_column_index:].isin([0]).all(axis=1)]

    export_df.to_csv(path, sep=';', index=False)


def export_single_dataset_to_json(dataset, path):
    """Function that exports the given dataframe with calculation results to a json file formatted according to the
     teco_json format in the location given by path

    Parameters
    ----------
    dataset : EpdDataset
        Instance of EpdDataset
    path : str
        Path to location where exported file is created containing filename
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), (dataset._name + ".json"))

    temp_uuid = str(uuid.uuid1())
    # add ref_flow attributes here when meta-data is passed by dunder methods in EpdDataset
    export_dict = {temp_uuid: {'name': str(dataset._name),
                               'ref_flow': {
                                   'value': '',
                                   'unit': ''
                               }}}

    for indicator_index, indicator in enumerate(dataset.environmental_indicators):
        export_dict[temp_uuid][indicator.abbreviation] = {'unit': indicator.unit}
        for stage_index, stage in enumerate(dataset.life_cycle_stages):
            if dataset._data[indicator_index][stage_index] != 0.0:
                export_dict[temp_uuid][indicator.abbreviation][stage.abbreviation] = dataset._data[indicator_index][
                    stage_index]

    with open(path, 'w') as f:
        json.dump(export_dict, f, indent=4, separators=(',', ': '))
