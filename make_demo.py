"""SYNTHETIC GCOV-format fixture only; this is NOT a NASA observation."""
import h5py
import numpy as np

rng = np.random.default_rng(12)
y, x = np.indices((260, 420))
db = -18 + 9 * np.exp(-((x - 240)**2 / 3500 + (y - 130)**2 / 4800))
db += 3 * (x > 50) * (x < 145) * (y > 80) * (y < 220)
db += rng.normal(0, 1.2, size=x.shape)
power = (10**(db / 10)).astype("float32")
power[:10, :10] = 0
with h5py.File("demo_only_not_satellite_data.h5", "w") as f:
    ds = f.create_dataset("science/LSAR/GCOV/grids/frequencyA/HHHH", data=power, compression="gzip")
    ds.attrs["units"] = "1"
    f.attrs["NOTE"] = "Synthetic data for verifying plotting code only; NOT a real NASA/NISAR product"
print("Created SYNTHETIC GCOV-style fixture.")
