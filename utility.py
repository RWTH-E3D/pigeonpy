"""Module containing utility functions"""


def linear_interpolate(dataset1, dataset2, steps, return_datasets=True):
    """

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
    array1 = dataset1._data
    array2 = dataset2._data
    interpolation_results = []

    for i in range(1, steps):
        interpolated_array = array1 + i * (array2 - array1) / steps
        if return_datasets:
            interpolated_dataset = type(dataset1)()
            interpolated_dataset._data = interpolated_array
            interpolated_dataset._name = f"_interpolated_dataset_{i}"
            interpolation_results.append(interpolated_dataset)
        else:
            interpolation_results.append(interpolated_array)

    return interpolation_results
