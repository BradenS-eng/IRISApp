import unittest

import numpy as np

from inverse_model import fit_in_plane_conductivity, flux_boundary_profile


class InverseModelTests(unittest.TestCase):
    def test_fit_recovers_synthetic_conductivity(self):
        thickness_m = 0.001
        length_m = 0.04
        h_air = 12.0
        ambient_c = 21.2
        m_expected = 80.0
        k_expected = 2.0 * h_air / (thickness_m * m_expected**2)

        x_scaled = np.linspace(0.0, 1.0, 201)
        phi = flux_boundary_profile(x_scaled, m_expected, thickness_m, length_m)
        profile_c = ambient_c + phi * 20.0

        fit = fit_in_plane_conductivity(
            profile_c,
            ambient_temp_c=ambient_c,
            thickness_m=thickness_m,
            length_m=length_m,
            air_convection_w_m2k=h_air,
        )

        self.assertAlmostEqual(fit["m_fit"], m_expected, places=4)
        self.assertAlmostEqual(fit["conductivity_w_mk"], k_expected, places=4)
        self.assertLess(fit["rmse"], 1e-10)


if __name__ == "__main__":
    unittest.main()
