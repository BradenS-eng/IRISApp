"""Create a schematic of the reported bake and thermal-cycling protocols.

This figure represents the prescribed temperature programs, not measured
specimen-temperature histories.  Both heating and cooling rates are 10 K/min.
"""

import matplotlib.pyplot as plt
import numpy as np

from settings import output_path


PNG_OUTPUT = output_path("TiPG_HIP_thermal_exposure_and_cycling_protocol.png")
SVG_OUTPUT = output_path("TiPG_HIP_thermal_exposure_and_cycling_protocol.svg")
PDF_OUTPUT = output_path("TiPG_HIP_thermal_exposure_and_cycling_protocol.pdf")

T_ROOM_K = 298.0
T_MAX_K = 550.0
RAMP_RATE_K_PER_MIN = 10.0
BAKE_DWELL_MIN = 60.0
RAMP_DURATION_MIN = (T_MAX_K - T_ROOM_K) / RAMP_RATE_K_PER_MIN
CYCLE_DURATION_MIN = 2.0 * RAMP_DURATION_MIN


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "font.size": 15,
            "axes.labelsize": 17,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "legend.fontsize": 13,
            "svg.fonttype": "none",
        }
    )


def style_axes(axis: plt.Axes) -> None:
    axis.set_ylim(280, 575)
    axis.set_yticks([298, 400, 500, 550])
    axis.grid(True, color="#b0b0b0", linewidth=0.8, alpha=0.75)
    for spine in axis.spines.values():
        spine.set_color("black")
        spine.set_linewidth(1.0)


def main() -> None:
    configure_style()
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(11.5, 4.7), dpi=200)

    # (a): The bake has the same ramps as one cycle, but a 60 min upper dwell.
    one_cycle_time = np.array([0.0, RAMP_DURATION_MIN, CYCLE_DURATION_MIN])
    one_cycle_temperature = np.array([T_ROOM_K, T_MAX_K, T_ROOM_K])
    bake_time = np.array(
        [0.0, RAMP_DURATION_MIN, RAMP_DURATION_MIN + BAKE_DWELL_MIN,
         CYCLE_DURATION_MIN + BAKE_DWELL_MIN]
    )
    bake_temperature = np.array([T_ROOM_K, T_MAX_K, T_MAX_K, T_ROOM_K])

    ax_a.plot(
        bake_time,
        bake_temperature,
        color="#c1121f",
        linewidth=2.8,
        label="Bake exposure (60 min dwell)",
    )
    ax_a.plot(
        one_cycle_time,
        one_cycle_temperature,
        color="#1d4e89",
        linewidth=2.4,
        linestyle="--",
        label="One thermal cycle (no dwell)",
    )
    ax_a.axvspan(
        RAMP_DURATION_MIN,
        RAMP_DURATION_MIN + BAKE_DWELL_MIN,
        color="#c1121f",
        alpha=0.09,
        zorder=0,
    )
    ax_a.annotate(
        "60 min at 550 K",
        xy=(RAMP_DURATION_MIN + BAKE_DWELL_MIN / 2, T_MAX_K),
        xytext=(0, 15),
        textcoords="offset points",
        ha="center",
        va="bottom",
        color="#8f0d16",
        fontsize=13,
    )
    ax_a.annotate(
        "10 K/min heating and cooling",
        xy=(RAMP_DURATION_MIN / 2, (T_ROOM_K + T_MAX_K) / 2),
        xytext=(8, -32),
        textcoords="offset points",
        ha="left",
        fontsize=12,
        color="#333333",
        arrowprops={"arrowstyle": "-", "color": "#555555", "lw": 0.8},
    )
    ax_a.text(0.02, 0.96, "(a)", transform=ax_a.transAxes, va="top", fontweight="bold")
    ax_a.set_xlabel("Program time (min)")
    ax_a.set_ylabel("Specified temperature (K)")
    ax_a.set_xlim(0, bake_time[-1] + 5)
    style_axes(ax_a)
    ax_a.legend(loc="lower right", frameon=True, borderpad=0.35, handlelength=2.3)

    # (b): Repeated no-dwell cycles; vertical markers indicate cumulative states tested.
    time = np.empty(2 * 10 + 1)
    temperature = np.empty_like(time)
    time[0] = 0.0
    temperature[0] = T_ROOM_K
    for i in range(10):
        time[2 * i + 1] = i * CYCLE_DURATION_MIN + RAMP_DURATION_MIN
        temperature[2 * i + 1] = T_MAX_K
        time[2 * i + 2] = (i + 1) * CYCLE_DURATION_MIN
        temperature[2 * i + 2] = T_ROOM_K
    ax_b.plot(time, temperature, color="#1d4e89", linewidth=2.2)
    for cycles in (1, 2, 5, 10):
        x = cycles * CYCLE_DURATION_MIN
        ax_b.axvline(x, color="#555555", linestyle=":", linewidth=1.0, zorder=0)
        ax_b.scatter(x, T_ROOM_K, s=34, color="#1d4e89", zorder=3, clip_on=False)
        ax_b.annotate(
            str(cycles),
            xy=(x, T_ROOM_K),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )
    ax_b.text(
        0.98,
        0.91,
        "Markers: IR measurement after\nindicated cumulative cycle count",
        transform=ax_b.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        bbox={"boxstyle": "square,pad=0.25", "facecolor": "white", "edgecolor": "#555555"},
    )
    ax_b.text(0.02, 0.96, "(b)", transform=ax_b.transAxes, va="top", fontweight="bold")
    ax_b.set_xlabel("Cumulative program time (min)")
    ax_b.set_ylabel("Specified temperature (K)")
    ax_b.set_xlim(0, 10 * CYCLE_DURATION_MIN)
    style_axes(ax_b)

    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.96, wspace=0.27)
    for output in (PNG_OUTPUT, SVG_OUTPUT, PDF_OUTPUT):
        fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {PNG_OUTPUT}")
    print(f"Saved {SVG_OUTPUT}")
    print(f"Saved {PDF_OUTPUT}")


if __name__ == "__main__":
    main()
