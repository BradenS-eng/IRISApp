"""Generate final-frame HIP temperature profiles before and after thermal cycling."""

import csv
import gc

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy.ndimage import gaussian_filter1d

from settings import data_root, output_path


DATA_ROOT = data_root()
OUTPUT = output_path(
    "IRIS_Ti_TF094-099_TF126-130_TF137_last500-frame-average_no-legend.png"
)
STATS_OUTPUT = output_path(
    "IRIS_Ti_TF094-099_TF126-130_TF137_last500-vs-final-frame_profile-differences.csv"
)
FIN_WIDTH_MM = 90.28
HEADER_BYTES = 2880
PIXEL_DTYPE = ">f4"
EDGE_SENSITIVITY_PX = 125
AVERAGED_FRAME_COUNT = 500
GEOMETRY_FRAME_COUNT = 10

# Solid: HIP sample before thermal cycling. Dashed: the same HIP sample after one cycle.
CASES = (
    ("IRIS-TF-094", 30, "#8000ff", "-"),
    ("IRIS-TF-095", 40, "#1e9bff", "-"),
    ("IRIS-TF-096", 50, "#40e0d0", "-"),
    ("IRIS-TF-097", 60, "#98ee90", "-"),
    ("IRIS-TF-098", 70, "#ff7f3f", "-"),
    ("IRIS-TF-099", 80, "#ff0000", "-"),
    ("IRIS-TF-137", 30, "#8000ff", "--"),
    ("IRIS-TF-126", 40, "#1e9bff", "--"),
    ("IRIS-TF-127", 50, "#40e0d0", "--"),
    ("IRIS-TF-128", 60, "#98ee90", "--"),
    ("IRIS-TF-129", 70, "#ff7f3f", "--"),
    ("IRIS-TF-130", 80, "#ff0000", "--"),
)


def mode_int(values: np.ndarray) -> int:
    values = np.asarray(values, dtype=int)
    return int(np.bincount(values[values >= 0]).argmax())


def extract_centerline_profile(
    heatmap: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, int, int, int]:
    # This matches the horizontal tube-fin edge/profile extraction used for Fig. data.
    vertical_gradient = np.gradient(heatmap, axis=0)
    top_edge = mode_int(np.argmax(vertical_gradient, axis=0))
    bottom_edge = mode_int(np.argmin(vertical_gradient, axis=0))

    fin_rows = heatmap[top_edge:bottom_edge, :]
    smoothed_rows = gaussian_filter1d(fin_rows, sigma=1, axis=1)
    offset = 5
    left_window = smoothed_rows[:, offset : offset + EDGE_SENSITIVITY_PX]
    right_window = smoothed_rows[:, -(offset + EDGE_SENSITIVITY_PX) : -offset]
    left_edges = offset + np.argmax(np.gradient(left_window, axis=1), axis=1)
    right_edges = (
        heatmap.shape[1]
        - offset
        - EDGE_SENSITIVITY_PX
        + np.argmin(np.gradient(right_window, axis=1), axis=1)
    )
    left_edge = mode_int(left_edges)
    right_edge = mode_int(right_edges)
    centerline_row = int((top_edge + bottom_edge) / 2)

    temperature_c = heatmap[centerline_row, left_edge:right_edge]
    lateral_position_mm = np.linspace(0, FIN_WIDTH_MM, temperature_c.size)
    return lateral_position_mm, temperature_c, centerline_row, left_edge, right_edge


def load_steady_state_profile(
    test_id: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = DATA_ROOT / test_id / f"{test_id}.fts"
    with fits.open(path, memmap=True) as hdul:
        shape = hdul[0].data.shape
    frames = np.memmap(
        path, dtype=PIXEL_DTYPE, mode="r", offset=HEADER_BYTES, shape=shape
    )
    stack = np.asarray(frames[-AVERAGED_FRAME_COUNT:], dtype=np.float32)
    geometry_map = np.mean(stack[-GEOMETRY_FRAME_COUNT:], axis=0, dtype=np.float64)
    x_mm, _, centerline_row, left_edge, right_edge = extract_centerline_profile(geometry_map)
    temperature_c = np.mean(stack[:, centerline_row, left_edge:right_edge], axis=0, dtype=np.float64)
    final_frame_temperature_c = np.asarray(
        stack[-1, centerline_row, left_edge:right_edge], dtype=np.float64
    )
    del frames
    return x_mm, temperature_c, final_frame_temperature_c


def main() -> None:
    profiles = []
    for test_id, inlet_temperature_c, color, linestyle in CASES:
        x_mm, temperature_c, final_frame_temperature_c = load_steady_state_profile(test_id)
        profiles.append(
            (test_id, inlet_temperature_c, color, linestyle, x_mm, temperature_c, final_frame_temperature_c)
        )
        difference_c = temperature_c - final_frame_temperature_c
        print(
            f"{test_id}: {inlet_temperature_c} C, n={temperature_c.size}, "
            f"mean={np.nanmean(difference_c):+.3f} C, "
            f"rmse={np.sqrt(np.nanmean(difference_c**2)):.3f} C, "
            f"max_abs={np.nanmax(np.abs(difference_c)):.3f} C"
        )
        gc.collect()

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 20,
            "axes.labelsize": 20,
            "axes.titlesize": 20,
            "xtick.labelsize": 20,
            "ytick.labelsize": 20,
        }
    )
    fig, ax = plt.subplots(figsize=(8.05, 6.04), dpi=100)
    for _, _, color, linestyle, x_mm, temperature_c, _ in sorted(
        profiles, key=lambda item: (item[1], item[3] == "--"), reverse=True
    ):
        ax.plot(x_mm, temperature_c, color=color, linestyle=linestyle, linewidth=2)

    ax.set_xlabel("Lateral Position Across Fin (mm)")
    ax.xaxis.labelpad = 0
    ax.set_ylabel(f"Temperature ({chr(176)}C)")
    ax.set_xlim(0, FIN_WIDTH_MM)
    ax.set_ylim(20, 80)
    ax.grid(True, color="#b0b0b0", linewidth=1, alpha=0.85)
    ax.text(0.01, 1.05, "Filleted Side", transform=ax.transAxes, va="top", ha="left")
    ax.text(0.99, 1.05, "Chamfered Side", transform=ax.transAxes, va="top", ha="right")
    # Match the reference IRIS_Ti.png axes geometry on an 806 x 604 canvas.
    fig.subplots_adjust(left=0.125, right=0.90, bottom=0.11, top=0.88)
    fig.savefig(OUTPUT)
    with STATS_OUTPUT.open("w", newline="", encoding="ascii") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["test_id", "inlet_temperature_c", "mean_difference_c", "rmse_c", "max_abs_difference_c"]
        )
        for test_id, inlet_temperature_c, _, _, _, temperature_c, final_frame_temperature_c in profiles:
            difference_c = temperature_c - final_frame_temperature_c
            writer.writerow(
                [
                    test_id,
                    inlet_temperature_c,
                    f"{np.nanmean(difference_c):.6f}",
                    f"{np.sqrt(np.nanmean(difference_c**2)):.6f}",
                    f"{np.nanmax(np.abs(difference_c)):.6f}",
                ]
            )
    print(f"Saved {OUTPUT}")
    print(f"Saved {STATS_OUTPUT}")


if __name__ == "__main__":
    main()
