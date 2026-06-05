import numpy as np
from scipy.optimize import curve_fit


class InverseFitError(ValueError):
    pass


def flux_boundary_profile(x_scaled, m_value, thickness_m, length_m):
    """Scaled 1D fin profile for a heat-flux boundary at x = 0.

    This follows the inverse model used in Section III.C of the ITHERM 2026
    manuscript. The measured temperature profile is scaled by theta(L), so the
    fitted profile is independent of the applied heat load.
    """
    x_scaled = np.asarray(x_scaled, dtype=float)
    argument = m_value * length_m * (1.0 - x_scaled)
    return (
        m_value * thickness_m / 2.0 * np.sinh(argument)
        + np.cosh(argument)
    )


def temperature_boundary_profile(x_scaled, m_value, thickness_m, length_m):
    """Scaled 1D fin profile for a constant-temperature boundary at x = 0."""
    x_scaled = np.asarray(x_scaled, dtype=float)
    denominator = (
        np.cosh(m_value * length_m)
        + m_value * thickness_m / 2.0 * np.sinh(m_value * length_m)
    )
    return flux_boundary_profile(x_scaled, m_value, thickness_m, length_m) / denominator


def fit_in_plane_conductivity(
    temperature_profile_c,
    ambient_temp_c,
    thickness_m,
    length_m,
    air_convection_w_m2k,
    initial_m=80.0,
    boundary_mode="flux",
    boundary_temp_c=None,
):
    """Fit effective in-plane thermal conductivity from a temperature profile.

    The model solves the steady 1D fin equation

        k H d2T/dx2 - 2 h (T - T_inf) = 0

    with m^2 = 2 h / (k H). The least-squares fit estimates m, then computes
    k = 2 h / (H m^2). This is an effective, system-level conductivity that
    can include contact resistance, geometric spreading, and interface effects;
    it should not be interpreted as an intrinsic material property.
    """
    profile = np.asarray(temperature_profile_c, dtype=float)
    profile = profile[np.isfinite(profile)]

    if profile.size < 5:
        raise InverseFitError("At least five finite temperature points are required.")
    if thickness_m <= 0 or length_m <= 0 or air_convection_w_m2k <= 0:
        raise InverseFitError("Thickness, length, and air convection coefficient must be positive.")

    x_scaled = np.linspace(0.0, 1.0, profile.size)
    boundary_mode = boundary_mode.lower().strip()

    if boundary_mode == "temperature":
        if boundary_temp_c is None:
            raise InverseFitError("Temperature-boundary fitting requires a boundary temperature.")
        denominator = boundary_temp_c - ambient_temp_c
        model = lambda x, m_value: temperature_boundary_profile(
            x, m_value, thickness_m, length_m
        )
    elif boundary_mode == "flux":
        boundary_temp = profile[-1] if boundary_temp_c is None else boundary_temp_c
        denominator = boundary_temp - ambient_temp_c
        model = lambda x, m_value: flux_boundary_profile(
            x, m_value, thickness_m, length_m
        )
    else:
        raise InverseFitError("Boundary mode must be 'flux' or 'temperature'.")

    if abs(denominator) < 1e-9:
        raise InverseFitError("Boundary and ambient temperatures are too close to normalize.")

    phi = (profile - ambient_temp_c) / denominator

    try:
        fit_params, _ = curve_fit(
            model,
            x_scaled,
            phi,
            p0=[initial_m],
            bounds=(1e-9, np.inf),
            maxfev=10000,
        )
    except Exception as exc:
        raise InverseFitError(f"Least-squares fit did not converge: {exc}") from exc
    m_fit = float(fit_params[0])
    phi_fit = model(x_scaled, m_fit)
    residuals = phi - phi_fit
    residual_sum_squares = float(np.sum(residuals**2))
    total_sum_squares = float(np.sum((phi - np.mean(phi))**2))
    r_squared = (
        1.0 - residual_sum_squares / total_sum_squares
        if total_sum_squares > 0
        else np.nan
    )
    rmse = float(np.sqrt(np.mean(residuals**2)))
    conductivity_w_mk = float(
        2.0 * air_convection_w_m2k / (thickness_m * m_fit**2)
    )

    return {
        "x_scaled": x_scaled,
        "temperature_profile_c": profile,
        "phi": phi,
        "phi_fit": phi_fit,
        "m_fit": m_fit,
        "conductivity_w_mk": conductivity_w_mk,
        "rmse": rmse,
        "r_squared": r_squared,
        "residual_sum_squares": residual_sum_squares,
        "boundary_mode": boundary_mode,
        "ambient_temp_c": ambient_temp_c,
        "boundary_temp_c": boundary_temp_c,
        "thickness_m": thickness_m,
        "length_m": length_m,
        "air_convection_w_m2k": air_convection_w_m2k,
    }
