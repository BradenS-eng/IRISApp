"""Generate the HIP pre-thermal-cycling temperature-profile comparison."""

from pathlib import Path

import generate_hip_thermal_cycle_comparison as profile_plot


profile_plot.OUTPUT = Path(__file__).with_name(
    "IRIS_HIP_precycle_TF094-099_last500-frame-average_no-legend.png"
)
profile_plot.STATS_OUTPUT = Path(__file__).with_name(
    "IRIS_HIP_precycle_TF094-099_last500-vs-final-frame_profile-differences.csv"
)
profile_plot.CASES = (
    ("IRIS-TF-094", 30, "#8000ff", "-"),
    ("IRIS-TF-095", 40, "#1e9bff", "-"),
    ("IRIS-TF-096", 50, "#40e0d0", "-"),
    ("IRIS-TF-097", 60, "#98ee90", "-"),
    ("IRIS-TF-098", 70, "#ff7f3f", "-"),
    ("IRIS-TF-099", 80, "#ff0000", "-"),
)


if __name__ == "__main__":
    profile_plot.main()
