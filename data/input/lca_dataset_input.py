"""Module contains functions to load lca datasets from the file/ dataset bindings of the dataclass"""


def load_lca_dataset_json(lca_dataset_object, given_lca_id, data_class):
    """Loads the metadata and indicator values from the dataset specified with the lca id from the
    teco json binding of the DataClass instance into the _data attribute of the passed instance of
    the dataset object

    Parameters
    ----------
    lca_dataset_object : En15804A1Dataset (or En15804A2Dataset when implemented)
        instance the dataset of the given lca id
    given_lca_id : str
        String with LCA id for the dataset to be loaded
    data_class : DataClass
        Instance of DataClass with file and data bindings

    """

    lca_data_bind = data_class.lca_data_bind

    try:
        lca_dataset_bind = lca_data_bind[given_lca_id]
        lca_dataset_object.epd_data_id = given_lca_id
        lca_dataset_object._name = lca_dataset_bind["name"]
        lca_dataset_object.ref_flow_unit = lca_dataset_bind["ref_flow"]["unit"]
        lca_dataset_object.ref_flow_value = lca_dataset_bind["ref_flow"]["value"]

    except KeyError:
        raise Exception(f"No dataset for combination of given lca id '{given_lca_id}', file format "
                        f"'{data_class.file_format}' and standard En15804+{lca_dataset_object.used_standard} was found. "
                        f"Please enter a valid lca id or try another file format.")

    for indicator_index, indicator in enumerate(lca_dataset_object.environmental_indicators):
        if indicator.abbreviation in lca_dataset_bind.keys():
            for stage_index, stage in enumerate(lca_dataset_object.life_cycle_stages):
                if stage.abbreviation in lca_dataset_bind[indicator.abbreviation]:
                    lca_dataset_object._data[indicator_index][stage_index] = float(
                        (lca_dataset_bind[indicator.abbreviation][stage.abbreviation]))
                elif (stage.abbreviation == "a1_a3") and (
                        "a1_a3" not in lca_dataset_bind[indicator.abbreviation]):
                    # Alle vorhandene Werte werden aufaddiert
                    # Warnung: Bei Verrechnung mit anderen Datensätzen wird die stage a1_a3 im Ergebnis Datensatz
                    # nicht mehr die Summe aus a1,a2,a3 ergeben
                    try:
                        lca_dataset_object._data[indicator_index][stage_index] = float(
                            lca_dataset_bind[indicator.abbreviation]["a1"]
                            + lca_dataset_bind[indicator.abbreviation]["a2"]
                            + lca_dataset_bind[indicator.abbreviation]["a3"]
                        )
                    except KeyError as Error:
                        print(f"Stage a1_a3 of dataset '{(lca_dataset_bind['name'])}' with id: '{given_lca_id}' for "
                              f"indicator '{indicator.abbreviation}' is calculated without stage {Error},"
                              f"because it is not contained in the dataset.")
                        lca_dataset_object._data[indicator_index][stage_index] = float(
                            lca_dataset_bind[indicator.abbreviation].get("a1", 0.0)
                            + lca_dataset_bind[indicator.abbreviation].get("a2", 0.0)
                            + lca_dataset_bind[indicator.abbreviation].get("a3", 0.0)
                        )


def load_lca_dataset_csv(lca_dataset_object, given_lca_id, data_class):
    """Loads the metadata and indicator values from the dataset specified with the lca id from the
    CSV binding (Oekobaudat database) of the DataClass instance into the _data attribute of the passed
    instance of the dataset object

    Parameters
    ----------
    lca_dataset_object : En15804A1Dataset (or En15804A2Dataset when implemented)
        instance the dataset of the given lca id
    given_lca_id : str
        String with LCA id for the dataset to be loaded
    data_class : DataClass
        Instance of DataClass

    """

    try:
        lca_dataset_mask = data_class.lca_data_bind['UUID'].values == given_lca_id
        lca_dataset_bind = data_class.lca_data_bind[lca_dataset_mask]

        lca_dataset_object.epd_data_id = given_lca_id
        lca_dataset_object._name = lca_dataset_bind['Name (de)'].iloc[0]
        lca_dataset_object.ref_flow_unit = lca_dataset_bind['Bezugseinheit'].iloc[0]
        lca_dataset_object.ref_flow_value = lca_dataset_bind['Bezugsgroesse'].iloc[0]
    except IndexError:
        raise Exception(f"No dataset for combination of given lca id '{given_lca_id}', file format "
                        f"'{data_class.file_format}' and standard En15804+{lca_dataset_object.used_standard} was found. "
                        f"Please enter a valid lca id or try another file format.")

    for indicator_index, indicator in enumerate(lca_dataset_object.environmental_indicators):
        for stage_index, stage in enumerate(lca_dataset_object.life_cycle_stages):
            if stage.abbreviation in lca_dataset_bind['Modul'].values:
                lca_dataset_object._data[indicator_index][stage_index] = lca_dataset_bind.loc[
                    lca_dataset_bind['Modul'] == stage.abbreviation, indicator.abbreviation.upper()].values[0]

            elif (stage.abbreviation == "a1_a3") and ("a1_a3" not in lca_dataset_bind['Modul']):
                # Nicht vorhandene Werte beim aufaddieren von a1,a2,a3 zu a1_a3 werden durch den default=0.0 ersetzt
                # Warnung: Bei Verrechnung mit anderen Datensätzen wird die stage a1_a3 im Ergebnis Datensatz
                # nicht mehr die Summe aus a1,a2,a3 ergeben
                try:
                    # test_replace_NaN_with_default = lca_dataset_bind.loc[lca_dataset_bind['Modul'] == 'a1', indicator['abbreviation'].upper()].reset_index(drop=True).get(0, default=0.0)
                    lca_dataset_object._data[indicator_index][stage_index] = (
                            lca_dataset_bind.loc[
                                lca_dataset_bind['Modul'] == 'a1', indicator.abbreviation.upper()].item()
                            + lca_dataset_bind.loc[
                                lca_dataset_bind['Modul'] == 'a2', indicator.abbreviation.upper()].item()
                            + lca_dataset_bind.loc[
                                lca_dataset_bind['Modul'] == 'a3', indicator.abbreviation.upper()].item()
                    )
                except KeyError as Error:
                    print(f"Stage a1_a3 could not be calculated for dataset '{lca_dataset_object._name}'"
                          f" with ID '{given_lca_id}'. {Error}")
                except ValueError as Error:
                    print(f"Stage a1_a3 could not be calculated for dataset '{lca_dataset_object._name}'"
                          f" with ID '{given_lca_id}'. {Error}")

