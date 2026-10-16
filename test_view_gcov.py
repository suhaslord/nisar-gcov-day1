import h5py
import numpy as np
import pytest
from view_gcov import find_layers, sample_db, plot_layer

def make_mock(path):
    with h5py.File(path, "w") as f:
        f.create_dataset("science/LSAR/GCOV/grids/frequencyA/HHHH", data=[[1.0, .1], [0.0, .01]])
        f.create_dataset("science/LSAR/GCOV/grids/frequencyA/HHHV", data=np.ones((2, 2), dtype="complex64"))

def test_db_conversion(tmp_path):
    file = tmp_path / "tiny.h5"
    make_mock(file)
    with h5py.File(file, "r") as f:
        paths = find_layers(f)
        assert paths == ["/science/LSAR/GCOV/grids/frequencyA/HHHH"]
        db, step = sample_db(f[paths[0]])
    assert step == 1
    np.testing.assert_allclose([db[0, 0], db[0, 1], db[1, 1]], [0, -10, -20])
    assert np.isnan(db[1, 0])

def test_plot_output(tmp_path):
    file = tmp_path / "tiny.h5"
    make_mock(file)
    report = plot_layer(file, tmp_path / "out.png")
    assert report["valid_sample_count"] == 3
    assert (tmp_path / "out.png").stat().st_size > 1000
    assert (tmp_path / "out.json").exists()

def test_bad_inputs(tmp_path):
    file = tmp_path / "bad.h5"
    with h5py.File(file, "w") as f:
        f.create_dataset("science/LSAR/GCOV/grids/frequencyA/HHHH", data=np.ones((2, 2), dtype="complex64"))
    with pytest.raises(ValueError, match="real-valued"):
        plot_layer(file, tmp_path / "out.png")
    with h5py.File(tmp_path / "empty.h5", "w"):
        pass
    with pytest.raises(ValueError, match="No GCOV"):
        plot_layer(tmp_path / "empty.h5", tmp_path / "out.png")

def test_sampling(tmp_path):
    file = tmp_path / "larger.h5"
    with h5py.File(file, "w") as f:
        f.create_dataset("science/LSAR/GCOV/grids/frequencyA/HHHH", data=np.ones((500, 900), dtype="float32"))
        db, step = sample_db(f["science/LSAR/GCOV/grids/frequencyA/HHHH"], 120)
        assert max(db.shape) <= 120
        assert step == 8
