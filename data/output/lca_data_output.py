import pandas as pd
import json
import uuid
import os


def export_calculated_dataframe(df, path="lca_data_export.csv", file_format="csv", drop_rows=False):
    dir_path = os.path.dirname(__file__)
    if file_format == "teco_json":
        if path=="lca_data_export.csv":
            export_dataframe_to_teco_json(df=df, path=os.path.join(dir_path, "lca_data_export.json"))
        else:
            export_dataframe_to_csv(df=df, path=path)
    else:
        if path=="lca_data_export.csv":
            export_dataframe_to_csv(df=df, path=os.path.join(dir_path, path), drop_rows=drop_rows)
        else:
            export_dataframe_to_csv(df=df, path=path, drop_rows=drop_rows)


def export_dataframe_to_csv(df, path, drop_rows=False):
    header = ['name', 'module'] + [indicator.abbreviation for indicator in df[0].environmental_indicators]
    export_dataframe = pd.DataFrame(columns=header)
    for index, row in df.items():
        dataset = row
        temp_df = pd.DataFrame(data=dataset._data.transpose(),
                               index=[x for x in range(len(dataset.life_cycle_stages))],
                               columns=[indicator.abbreviation for indicator in dataset.environmental_indicators])

        temp_df.insert(0, "module", value=pd.Series([stage.abbreviation for stage in dataset.life_cycle_stages]))
        temp_df.insert(0, "name", value=str(index))

        # drop rows/ life cycle stages where all values are equal to zero
        if drop_rows:
            temp_df = temp_df[~temp_df.iloc[:, 2:].isin([0]).all(axis=1)]

        export_dataframe = pd.concat([export_dataframe, temp_df], ignore_index=True)

    export_dataframe.to_csv(path, sep=';', index=False)

def export_dataframe_to_teco_json(df, path):
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
                    temp_dict[temp_uuid][indicator.abbreviation][stage.abbreviation] = dataset._data[indicator_index][stage_index]

        export_dict.update(temp_dict)

    with open(path, 'w') as f:
        json.dump(export_dict, f, indent=4, separators=(',', ': '))


def export_single_dataset_to_csv(dataset, path, drop_rows=False):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), (dataset._name + ".csv"))

    export_df = pd.DataFrame(data=dataset._data.transpose(),
                 index=[x for x in range(len(dataset.life_cycle_stages))],
                 columns=[indicator.abbreviation for indicator in dataset.environmental_indicators])
    export_df.insert(0, "module", value=pd.Series([stage.abbreviation for stage in dataset.life_cycle_stages]))
    export_df.insert(0, "name", value=str(dataset._name))

    # drop rows/ life cycle stages where all values are equal to zero
    if drop_rows:
        export_df = export_df[~export_df.iloc[:, 2:].isin([0]).all(axis=1)]

    export_df.to_csv(path, sep=';', index=False)

def export_single_dataset_to_json(dataset, path):
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

