"""Small GCOV backscatter viewer. HDF5 diagonal covariance is linear power."""
import argparse
import json
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = "/science/LSAR/GCOV/grids"
LAYER_NAMES = ("HHHH", "HVHV", "VVVV", "VHVH", "RHRH", "RVRV")


def find_layers(h5):
    paths = []
    for frequency in ("frequencyA", "frequencyB"):
        for name in LAYER_NAMES:
            path = f"{BASE}/{frequency}/{name}"
            if path in h5 and isinstance(h5[path], h5py.Dataset) and h5[path].ndim == 2:
                paths.append(path)
    return paths


def sample_db(dataset, max_size=1200):
    if dataset.ndim != 2 or np.issubdtype(dataset.dtype, np.complexfloating):
        raise ValueError("Expected a real-valued 2D diagonal GCOV covariance term")
    step = max(1, int(np.ceil(max(dataset.shape) / max_size)))
    image = np.asarray(dataset[::step, ::step], dtype=float)
    invalid = ~np.isfinite(image) | (image <= 0)
    for key in ("_FillValue", "missing_value"):
        if key in dataset.attrs:
            for fill in np.asarray(dataset.attrs[key]).reshape(-1):
                if np.issubdtype(type(fill), np.number) and np.isfinite(fill):
                    invalid |= image == fill
    db = np.full(image.shape, np.nan)
    db[~invalid] = 10 * np.log10(image[~invalid])
    return db, step


def plot_layer(file, out, layer=None, max_size=1200):
    with h5py.File(file, "r") as h5:
        paths = find_layers(h5)
        if not paths:
            raise ValueError("No GCOV diagonal covariance layers found")
        name = layer or paths[0]
        if name not in paths:
            raise ValueError(f"Layer not available; choose from {paths}")
        source_shape = list(h5[name].shape)
        image, step = sample_db(h5[name], max_size)
        synthetic = "synthetic" in str(h5.attrs.get("NOTE", "")).lower()
    valid = image[np.isfinite(image)]
    if valid.size == 0:
        raise ValueError("No valid positive backscatter samples")
    lo, hi = np.percentile(valid, [2, 98])
    if hi <= lo:
        lo, hi = float(lo-1), float(hi+1)
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    plot = ax.imshow(image, cmap="gray", vmin=lo, vmax=hi, origin="upper", interpolation="nearest")
    ax.set_title(("SYNTHETIC DEMO - NOT SATELLITE DATA" if synthetic else "GCOV backscatter viewer") + f" | {name.rsplit('/', 1)[-1]}")
    ax.set_xlabel("Sampled column (not longitude)")
    ax.set_ylabel("Sampled row (not latitude)")
    fig.colorbar(plot, ax=ax, label="Gamma-zero intensity (dB)", shrink=.85)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    report = {"input": str(file), "layer": name, "source_shape": source_shape,
              "sample_shape": list(image.shape), "stride": step,
              "valid_sample_count": int(valid.size), "db_median": float(np.median(valid)),
              "is_synthetic_demo": synthetic, "real_nisar_scene_verified": False}
    Path(out).with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="GCOV diagonal backscatter (dB) viewer")
    parser.add_argument("file")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--out", default="backscatter.png")
    parser.add_argument("--layer")
    parser.add_argument("--max-size", type=int, default=1200)
    args = parser.parse_args()
    if args.max_size < 32:
        parser.error("max-size must be >= 32")
    if args.list:
        with h5py.File(args.file, "r") as h5:
            for path in find_layers(h5):
                print(path, h5[path].shape, h5[path].dtype)
        return
    result = plot_layer(args.file, args.out, args.layer, args.max_size)
    print(f"Saved {args.out} ({result['valid_sample_count']} valid samples)")


if __name__ == "__main__":
    main()
