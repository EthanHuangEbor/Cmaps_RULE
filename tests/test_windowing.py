import numpy as np
import pandas as pd

from rul_prediction.data import make_last_windows, make_sequence_windows


def test_window_shapes():
    df = pd.DataFrame(
        {
            "unit": [1, 1, 1, 1, 2, 2, 2, 2],
            "cycle": [1, 2, 3, 4, 1, 2, 3, 4],
            "sensor_1": np.arange(8),
            "sensor_2": np.arange(8) * 2,
            "rul": [3, 2, 1, 0, 3, 2, 1, 0],
        }
    )
    x, y, units, cycles = make_sequence_windows(df, ["sensor_1", "sensor_2"], window_size=3)
    assert x.shape == (4, 3, 2)
    assert y.tolist() == [1, 0, 1, 0]
    assert units.tolist() == [1, 1, 2, 2]
    assert cycles.tolist() == [3, 4, 3, 4]

    last_x, last_y, last_units, _ = make_last_windows(df, ["sensor_1", "sensor_2"], window_size=3)
    assert last_x.shape == (2, 3, 2)
    assert last_y.tolist() == [0, 0]
    assert last_units.tolist() == [1, 2]

