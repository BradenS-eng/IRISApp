"""Generate the Ti-only final-500-frame average temperature-profile comparison."""

from pathlib import Path

import generate_ti_only_comparison as profile_plot


profile_plot.OUTPUT = Path(__file__).with_name(
    "IRIS_Ti_only_TF077-081_TF084_last500-frame-average.png"
)
profile_plot.NO_LEGEND_OUTPUT = Path(__file__).with_name(
    "IRIS_Ti_only_TF077-081_TF084_last500-frame-average_no-legend.png"
)
profile_plot.STATS_OUTPUT = Path(__file__).with_name(
    "IRIS_Ti_only_TF077-081_TF084_last500-vs-final-frame_profile-differences.csv"
)
profile_plot.CASES = (
    ("IRIS-TF-077", 30, "#8000ff"),
    ("IRIS-TF-078", 40, "#1e9bff"),
    ("IRIS-TF-079", 50, "#40e0d0"),
    ("IRIS-TF-080", 60, "#98ee90"),
    ("IRIS-TF-081", 70, "#ff7f3f"),
    ("IRIS-TF-084", 80, "#ff0000"),
)


if __name__ == "__main__":
    profile_plot.main()
