# Tiny NISAR GCOV backscatter viewer

A small, one-day Python project to learn how NISAR GCOV backscatter images work. It reads a **2-D real-valued diagonal covariance layer** (`HHHH`, `HVHV`, `VVVV`, etc.) in a NISAR GCOV `.h5` file, converts calibrated gamma-zero **power** to decibels with `10 * log10(power)` and draws a grayscale image.

**This is only a quick viewer, not a SAR analysis result.** The bundled example is *synthetic*, **not** a NISAR scene. The script is tested on local synthetic HDF5 fixtures, but a genuine NISAR GCOV science file has **not** been downloaded or processed here. No georeferencing, calibration checks, classification, change detection, or scientific validation is claimed.

## Try the tiny demo

```bash
python -m pip install -r requirements.txt
python make_demo.py
python view_gcov.py demo_only_not_satellite_data.h5 --out demo_backscatter.png
python -m pip install pytest  # optional, only needed to rerun tests
python -m pytest -q test_view_gcov.py
```

The script saves a PNG and a sidecar JSON containing the chosen path, sample count, sampling stride, and display range. Demo generated data is labelled SYNTHETIC in its HDF5 attributes; the output is not a valid satellite map.

## Try a real NISAR GCOV product

1. Download an official GCOV `.h5` via [ASF Vertex GCOV search](https://search.asf.alaska.edu/#/?dataset=NISAR&sciProducts=GCOV). NASA Earthdata Login may be required. ASF's [sample data](https://asf.alaska.edu/working-with-nisar-sample-data/) includes **prelaunch simulated sample** GCOV files, distinct from satellite acquisitions. Some genuine GCOV files are very large.
2. Run `python view_gcov.py downloaded_scene.h5 --list` to check available datasets.
3. Run `python view_gcov.py downloaded_scene.h5 --out backscatter.png` (uses the first available polarization), or supply `--layer /science/LSAR/GCOV/grids/frequencyA/HHHH` explicitly.

This viewer reads a regular subsample from the input HDF5 file before converting it, to avoid loading an entire large scene. The axes show **pixel/sample positions, not latitude/longitude**. If you want a real mapped output, incorporate GCOV geotransform/projection metadata or use GDAL.

## References

- [ASF NISAR GCOV product guide](https://nisar-docs.asf.alaska.edu/data-products/level-2/gcov/)
- [NASA NISAR sample data](https://science.nasa.gov/mission/nisar/sample-data/)
- [ASF NISAR sample-data walkthrough](https://asf.alaska.edu/working-with-nisar-sample-data/)

Written as a small learning exercise, not an official NASA/JPL project.