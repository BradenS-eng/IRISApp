"""Create a presentation-focused replacement for manuscript Fig. 4.

The figure uses the measured sensor histories and a 500-frame average from
IRIS-TF-084.  It is illustrative only; no heat-rejection or property estimate
is made from these data.
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.ndimage import gaussian_filter1d

from settings import data_root, output_path


TEST_ID = "IRIS-TF-084"
DATA_ROOT = data_root()
TEST_DIR = DATA_ROOT / TEST_ID
OUTPUT = output_path("Fig_4_revised.png")

FIN_LENGTH_MM = 90.28
FIN_WIDTH_MM = 34.02
FRAMES_TO_AVERAGE = 500
FITS_HEADER_BYTES = 2880
PIXEL_DTYPE = ">f4"
EDGE_WINDOW_PX = 125


def mode_int(values: np.ndarray) -> int:
    values = np.asarray(values, dtype=int)
    return int(np.bincount(values[values >= 0]).argmax())


def centerline_geometry(heatmap: np.ndarray) -> tuple[int, int, int, int, int]:
    """Return the centerline and detected fin bounds using IRISApp logic."""
    top = mode_int(np.argmax(np.gradient(heatmap, axis=0), axis=0))
    bottom = mode_int(np.argmin(np.gradient(heatmap, axis=0), axis=0))
    fin_rows = heatmap[top:bottom, :]
    smooth = gaussian_filter1d(fin_rows, sigma=1, axis=1)
    offset = 5
    left = offset + np.argmax(np.gradient(smooth[:, offset : offset + EDGE_WINDOW_PX], axis=1), axis=1)
    right = heatmap.shape[1] - offset - EDGE_WINDOW_PX + np.argmin(
        np.gradient(smooth[:, -(offset + EDGE_WINDOW_PX) : -offset], axis=1), axis=1
    )
    return int((top + bottom) / 2), mode_int(left), mode_int(right), top, bottom


def load_sensor_history() -> pd.DataFrame:
    """Parse Arduino records while omitting start-up and end-of-run log lines."""
    sensor_path = TEST_DIR / "sensors.txt"
    lines = sensor_path.read_text(encoding="utf-8").splitlines()
    header_index = next(i for i, line in enumerate(lines) if "Time_ms" in line)
    columns = lines[header_index].split("->", maxsplit=1)[1].strip().split(",")
    records: list[list[float]] = []
    for line in lines[header_index + 1 :]:
        if "->" not in line:
            continue
        payload = line.split("->", maxsplit=1)[1].strip()
        fields = payload.split(",")
        if len(fields) != len(columns):
            continue
        try:
            records.append([float(value) for value in fields])
        except ValueError:
            continue
    frame = pd.DataFrame(records, columns=columns)
    if frame.empty:
        raise ValueError(f"No sensor records found in {sensor_path}")
    frame["Time_s"] = (frame["Time_ms"] - frame["Time_ms"].iloc[0]) / 1000.0
    return frame


def load_flir_history(side: str) -> tuple[np.ndarray, np.ndarray]:
    path = TEST_DIR / f"{side}_Side_TC_Flir.txt"
    frame = pd.read_csv(path, sep="\t")
    time = pd.to_datetime(frame["time"], errors="raise")
    seconds = (time - time.iloc[0]).dt.total_seconds().to_numpy()
    values = frame.iloc[:, 2].to_numpy(dtype=float)
    return seconds, values


def load_time_averaged_thermograph() -> tuple[np.ndarray, tuple[int, int, int, int, int]]:
    fits_path = TEST_DIR / f"{TEST_ID}.fts"
    with fits.open(fits_path, memmap=True) as hdul:
        shape = hdul[0].data.shape
    frames = np.memmap(fits_path, dtype=PIXEL_DTYPE, mode="r", offset=FITS_HEADER_BYTES, shape=shape)
    thermograph = np.mean(np.asarray(frames[-FRAMES_TO_AVERAGE:], dtype=np.float32), axis=0)
    del frames
    return thermograph, centerline_geometry(thermograph)


def make_figure() -> None:
    history = load_sensor_history()
    chamfer_time, chamfer_flir = load_flir_history("Chamfered")
    fillet_time, fillet_flir = load_flir_history("Filleted")
    thermograph, (centerline, left, right, top, bottom) = load_time_averaged_thermograph()

    if right <= left or bottom <= top:
        raise ValueError("Detected fin bounds are invalid.")
    fin = thermograph[top:bottom, left:right]
    vmin = math.floor(float(np.nanmin(thermograph)))
    vmax = math.ceil(float(np.nanmax(thermograph)))
    ticks = np.linspace(vmin, vmax, 5)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 11,
            "axes.labelsize": 13,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 9.5,
        }
    )
    fig, (ax_history, ax_ir) = plt.subplots(2, 1, figsize=(7.5, 8.6), dpi=300)

    history_lines = [
        ax_history.plot(history["Time_s"], history["ChamferTemp_C"], color="#2e7d32", linewidth=1.4,
                        label="Chamfered edge, TC")[0],
        ax_history.plot(history["Time_s"], history["FilletTemp_C"], color="#c62828", linewidth=1.4,
                        label="Filleted edge, TC")[0],
        ax_history.plot(chamfer_time, chamfer_flir, color="#00a6b2", linewidth=1.1,
                        label="Chamfered edge, IR")[0],
        ax_history.plot(fillet_time, fillet_flir, color="#f59e0b", linewidth=1.1,
                        label="Filleted edge, IR")[0],
        ax_history.plot(history["Time_s"], history["FluidTemp_C"], color="#6a1b9a", linewidth=1.4,
                        label="Inlet-water temperature")[0],
    ]
    ax_flow = ax_history.twinx()
    flow_line = ax_flow.plot(history["Time_s"], history["FlowRate_L_per_min"], color="#1565c0", linewidth=1.2,
                             label="Flow rate")[0]

    ax_history.set_xlim(0, 300)
    ax_history.set_xlabel("Time (s)")
    ax_history.set_ylabel("Temperature (°C)")
    ax_history.set_ylim(32, 82)
    ax_history.grid(True, color="#b0b0b0", linewidth=0.8, alpha=0.85)
    ax_history.set_axisbelow(True)
    ax_flow.set_ylabel("Flow Rate (L/min)", color="#1565c0")
    ax_flow.tick_params(axis="y", colors="#1565c0")
    ax_flow.set_ylim(0.91, 0.99)
    ax_history.text(-0.15, 1.04, "(a)", transform=ax_history.transAxes, fontsize=15, va="bottom")

    fig.legend(
        history_lines + [flow_line],
        [line.get_label() for line in history_lines] + [flow_line.get_label()],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.997),
        ncol=3,
        frameon=True,
        borderpad=0.35,
        handlelength=1.8,
        columnspacing=1.2,
    )

    # Map the full camera field to millimetres relative to the detected fin
    # boundary; values outside 0--90.28 mm and 0--34.02 mm are surroundings.
    x_min = (0 - left) / (right - left) * FIN_LENGTH_MM
    x_max = (thermograph.shape[1] - left) / (right - left) * FIN_LENGTH_MM
    y_min = (bottom - thermograph.shape[0]) / (bottom - top) * FIN_WIDTH_MM
    y_max = (bottom - 0) / (bottom - top) * FIN_WIDTH_MM
    image = ax_ir.imshow(
        thermograph,
        cmap="turbo",
        origin="upper",
        extent=(x_min, x_max, y_min, y_max),
        vmin=vmin,
        vmax=vmax,
        aspect="equal",
    )
    centerline_y = (bottom - centerline) / (bottom - top) * FIN_WIDTH_MM
    ax_ir.plot((0, FIN_LENGTH_MM), (centerline_y, centerline_y), color="white", linestyle="--", linewidth=1.0)
    ax_ir.plot((0, FIN_LENGTH_MM, FIN_LENGTH_MM, 0, 0), (0, 0, FIN_WIDTH_MM, FIN_WIDTH_MM, 0),
               color="black", linestyle="--", linewidth=0.9)

    # These positions use the non-vertical-orientation mapping in IRISApp.
    filleted_tc = (27.65, 16.77)
    chamfered_tc = (FIN_LENGTH_MM - 28.47, FIN_WIDTH_MM - 16.71)
    for tc_x, tc_y in (filleted_tc, chamfered_tc):
        ax_ir.plot(tc_x, tc_y, marker="s", markersize=6, markerfacecolor="none",
                   markeredgecolor="black", markeredgewidth=1.4, linestyle="none")

    ax_ir.set_xlabel("Lateral Position Across Fin (mm)")
    ax_ir.set_ylabel("Transverse Position (mm)")
    ax_ir.text(0.01, 0.96, "Filleted side", transform=ax_ir.transAxes, ha="left", va="top",
               fontsize=12, color="white")
    ax_ir.text(0.99, 0.96, "Chamfered side", transform=ax_ir.transAxes, ha="right", va="top",
               fontsize=12, color="white")
    ax_ir.text(-0.15, 1.04, "(b)", transform=ax_ir.transAxes, fontsize=15, va="bottom")
    colorbar = fig.colorbar(image, ax=ax_ir, pad=0.02, fraction=0.045, ticks=ticks)
    colorbar.set_label("Temperature (°C)")
    colorbar.ax.set_yticklabels([f"{tick:.0f}" for tick in ticks])

    for axis in (ax_history, ax_ir):
        for spine in axis.spines.values():
            spine.set_color("black")
            spine.set_linewidth(1.0)

    fig.subplots_adjust(left=0.13, right=0.87, bottom=0.08, top=0.84, hspace=0.56)
    fig.savefig(OUTPUT, dpi=300)
    plt.close(fig)
    print(f"Test: {TEST_ID}")
    print(f"Detected fin bounds (left, right, top, bottom): {left}, {right}, {top}, {bottom}")
    print(f"Full-frame temperature range: {float(np.nanmin(thermograph)):.2f} to {float(np.nanmax(thermograph)):.2f} °C")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    make_figure()
