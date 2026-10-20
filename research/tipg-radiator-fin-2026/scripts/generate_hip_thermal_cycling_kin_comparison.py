"""Plot time-averaged HIP Ti-PG profiles across baking and thermal-cycle states."""

import gc

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy.ndimage import gaussian_filter1d

from settings import data_root, output_path


DATA_ROOT = data_root()
OUTPUT = output_path(
    "IRIS_TiPG_HIP_thermal_cycling_TF099_TF130_TF139_TF140_TF141_TF143_last500-frame-average.png"
)
FIN_WIDTH_MM = 90.28
HEADER_BYTES = 2880
PIXEL_DTYPE = ">f4"
EDGE_SENSITIVITY_PX = 125
AVERAGED_FRAME_COUNT = 500
GEOMETRY_FRAME_COUNT = 10

CASES = (
    ("IRIS-TF-099", "Pre-baking", "#264653", "-"),
    ("IRIS-TF-130", "Baked", "#e76f51", "-"),
    ("IRIS-TF-139", "1-cycle", "#2a9d8f", "-"),
    ("IRIS-TF-140", "2-cycle", "#6a4c93", "-"),
    ("IRIS-TF-141", "5-cycle", "#c1121f", "-"),
    ("IRIS-TF-143", "10-cycle", "#7f5539", "-"),
)


def mode_int(values: np.ndarray) -> int:
    values = np.asarray(values, dtype=int)
    return int(np.bincount(values[values >= 0]).argmax())


def extract_centerline_profile(
    heatmap: np.ndarray,
) -> tuple[np.ndarray, int, int, int]:
    vertical_gradient = np.gradient(heatmap, axis=0)
    top_edge = mode_int(np.argmax(vertical_gradient, axis=0))
    bottom_edge = mode_int(np.argmin(vertical_gradient, axis=0))

    fin_rows = heatmap[top_edge:bottom_edge, :]
    smoothed_rows = gaussian_filter1d(fin_rows, sigma=1, axis=1)
    offset = 5
    left_window = smoothed_rows[:, offset : offset + EDGE_SENSITIVITY_PX]
    right_window = smoothed_rows[:, -(offset + EDGE_SENSITIVITY_PX) : -offset]
    left_edge = mode_int(offset + np.argmax(np.gradient(left_window, axis=1), axis=1))
    right_edge = mode_int(
        heatmap.shape[1]
        - offset
        - EDGE_SENSITIVITY_PX
        + np.argmin(np.gradient(right_window, axis=1), axis=1)
    )
    centerline_row = int((top_edge + bottom_edge) / 2)
    lateral_position_mm = np.linspace(0, FIN_WIDTH_MM, right_edge - left_edge)
    return lateral_position_mm, centerline_row, left_edge, right_edge


def load_time_averaged_profile(test_id: str) -> tuple[np.ndarray, np.ndarray]:
    path = DATA_ROOT / test_id / f"{test_id}.fts"
    with fits.open(path, memmap=True) as hdul:
        shape = hdul[0].data.shape
    frames = np.memmap(path, dtype=PIXEL_DTYPE, mode="r", offset=HEADER_BYTES, shape=shape)
    stack = np.asarray(frames[-AVERAGED_FRAME_COUNT:], dtype=np.float32)
    geometry_map = np.mean(stack[-GEOMETRY_FRAME_COUNT:], axis=0, dtype=np.float64)
    x_mm, centerline_row, left_edge, right_edge = extract_centerline_profile(geometry_map)
    temperature_c = np.mean(
        stack[:, centerline_row, left_edge:right_edge], axis=0, dtype=np.float64
    )
    del frames
    gc.collect()
    return x_mm, temperature_c


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 20,
            "axes.labelsize": 20,
            "xtick.labelsize": 20,
            "ytick.labelsize": 20,
            "legend.fontsize": 15,
        }
    )
    fig, ax = plt.subplots(figsize=(8.05, 6.04), dpi=100)
    for test_id, label, color, linestyle in CASES:
        x_mm, temperature_c = load_time_averaged_profile(test_id)
        ax.plot(
            x_mm,
            temperature_c,
            color=color,
            linestyle=linestyle,
            linewidth=2,
            label=label,
        )

    ax.set_xlabel("Lateral Position Across Fin (mm)")
    ax.xaxis.labelpad = 0
    ax.set_ylabel(f"Temperature ({chr(176)}C)")
    ax.set_xlim(0, FIN_WIDTH_MM)
    ax.set_ylim(20, 80)
    ax.grid(True, color="#b0b0b0", linewidth=1, alpha=0.85)
    ax.text(0.01, 1.05, "Filleted Side", transform=ax.transAxes, va="top", ha="left")
    ax.text(0.99, 1.05, "Chamfered Side", transform=ax.transAxes, va="top", ha="right")
    ax.legend(
        loc="lower right",
        frameon=True,
        handlelength=1.0,
        handletextpad=0.35,
        borderpad=0.25,
        labelspacing=0.3,
    )
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("black")
        spine.set_linewidth(1.0)
    fig.subplots_adjust(left=0.125, right=0.90, bottom=0.11, top=0.88)
    fig.savefig(OUTPUT)
    plt.close(fig)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
