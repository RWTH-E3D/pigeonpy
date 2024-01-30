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

    if given_lca_id in lca_data_bind.keys():
        lca_dataset_bind = lca_data_bind[given_lca_id]
        lca_dataset_object.epd_data_id = given_lca_id
        lca_dataset_object._name = lca_dataset_bind["name"]
        lca_dataset_object.ref_flow_unit = lca_dataset_bind["ref_flow"]["unit"]
        lca_dataset_object.ref_flow_value = lca_dataset_bind["ref_flow"]["value"]
    else:
        print(f"No dataset for given lca id '{given_lca_id}' was found. Please enter a valid lca id.")
        return

    for indicator_index, indicator in enumerate(data_class.indicators_bind):
        if indicator["abbreviation"] in lca_dataset_bind.keys():
            for stage_index, stage in enumerate(data_class.life_cycle_stages_bind):
                if stage["abbreviation"] in lca_dataset_bind[indicator["abbreviation"]]:
                    lca_dataset_object._data[indicator_index][stage_index] = float(
                        (lca_dataset_bind[indicator["abbreviation"]][stage["abbreviation"]]))
                elif (stage["abbreviation"] == "a1_a3") and (
                        "a1_a3" not in lca_dataset_bind[indicator["abbreviation"]]):
                    # Nicht optimal, bestenfalls sollten die vorhandenen Werte aufaddiert werden, unabhängig davon
                    # welcher fehlt; Momentan: Falls einer der Werte nicht vorhanden ist, bricht die Berechnung für
                    # a1_a3 ab
                    try:
                        lca_dataset_object._data[indicator_index][stage_index] = float(
                            lca_dataset_bind[indicator["abbreviation"]]["a1"]
                            + lca_dataset_bind[indicator["abbreviation"]]["a2"]
                            + lca_dataset_bind[indicator["abbreviation"]]["a3"]
                        )
                    except KeyError as Error:
                        print(f"Life cycle stage a1_a3 for lca dataset id: '{given_lca_id}'/ "
                              f"{(lca_dataset_bind['name'])} and indicator {(indicator['abbreviation'])} could not be "
                              f"calculated and added to the data matrix because stage {Error} is missing.")


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

    if given_lca_id in data_class.lca_data_bind['UUID'].values:
        lca_dataset_mask = data_class.lca_data_bind['UUID'].values == given_lca_id
        lca_dataset_bind = data_class.lca_data_bind[lca_dataset_mask]

        lca_dataset_object.epd_data_id = given_lca_id
        lca_dataset_object._name = lca_dataset_bind['Name (de)'].iloc[0]
        lca_dataset_object.ref_flow_unit = lca_dataset_bind['Bezugseinheit'].iloc[0]
        lca_dataset_object.ref_flow_value = lca_dataset_bind['Bezugsgroesse'].iloc[0]
    else:
        print(f"No dataset for given lca id '{given_lca_id}' was found. Please enter a valid lca id")
        return

    for indicator_index, indicator in enumerate(data_class.indicators_bind):
        for stage_index, stage in enumerate(data_class.life_cycle_stages_bind):
            if stage['abbreviation'] in lca_dataset_bind['Modul'].values:
                lca_dataset_object._data[indicator_index][stage_index] = lca_dataset_bind.loc[
                    lca_dataset_bind['Modul'] == stage['abbreviation'], indicator['abbreviation'].upper()].values[0]

            elif (stage['abbreviation'] == "a1_a3") and ("a1_a3" not in lca_dataset_bind['Modul']):
                # Nicht optimal, bestenfalls sollten die vorhandenen Werte aufaddiert werden, unabhängig davon
                # welcher fehlt; Momentan: Falls einer der Werte nicht vorhanden ist, bricht die Berechnung für
                # a1_a3 ab
                try:
                    lca_dataset_object._data[indicator_index][stage_index] = (
                        lca_dataset_bind.loc[lca_dataset_bind['Modul'] == 'a1', indicator['abbreviation'].upper()].item()
                        + lca_dataset_bind.loc[lca_dataset_bind['Modul'] == 'a2', indicator['abbreviation'].upper()].item()
                        + lca_dataset_bind.loc[lca_dataset_bind['Modul'] == 'a3', indicator['abbreviation'].upper()].item()
                    )
                except KeyError as Error:
                    print(f"Life cycle stage a1_a3 for lca dataset id: '{given_lca_id}'/ "
                          f"{(lca_dataset_bind['name'])} and indicator {(indicator['abbreviation'])} could not be "
                          f"calculated and added to the data matrix because stage {Error} is missing.")
