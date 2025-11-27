import pytest
from formula_generator import (
    wavelength_to_band,
    parse_satellite_bands_table,
    convert_formula,
)

import pandas as pd

landsat_bands = parse_satellite_bands_table("specification/Спутники.xlsx")[
    "LANDSAT-89 OLITIRS"
]

emit_bands = parse_satellite_bands_table("specification/Спутники.xlsx")["EMIT"]


@pytest.mark.parametrize(
    "wl, expected_band",
    [
        (440, "SR_B1"),
        (480, "SR_B2"),
        (550, "SR_B3"),
        (655, "SR_B4"),
        (860, "SR_B5"),
        (1600, "SR_B6"),
        (2200, "SR_B7"),
        (500, "SR_B2"),  # граница SR_B2
        (670, "SR_B4"),  # граница SR_B4
    ],
)
def test_single_wavelength(wl, expected_band):
    assert wavelength_to_band(wl, wl, landsat_bands) == expected_band


@pytest.mark.parametrize(
    "wl_min, wl_max, expected_band",
    [
        (430, 450, "SR_B1"),  # полностью покрывает SR_B1
        (450, 510, "SR_B2"),  # полностью покрывает SR_B2
        (530, 590, "SR_B3"),  # полностью покрывает SR_B3
        (640, 670, "SR_B4"),  # полностью покрывает SR_B4
        (850, 880, "SR_B5"),  # полностью покрывает SR_B5
        (500, 680, "SR_B8"),  # диапазон полностью попадает в панхроматический
        (700, 710, "nan"),  # диапазон не покрыт ни одним мультиспектральным бэндом
    ],
)
def test_wavelength_range(wl_min, wl_max, expected_band):
    assert wavelength_to_band(wl_min, wl_max, landsat_bands) == expected_band


@pytest.mark.parametrize(
    "wl_min, wl_max, expected_band",
    [
        (377, 384, "B1"),  # диапазон полностью в B1
        (386, 395, "B2"),  # диапазон B2
        (400, 408, "B4"),  # перекрытие >50% с B4
    ],
)
def test_emit_wavelength_range(wl_min, wl_max, expected_band):
    assert wavelength_to_band(wl_min, wl_max, emit_bands) == expected_band


@pytest.mark.parametrize(
    "formula, expected_formula",
    [
        (
            "([1600:1700] - [2145:2185])/([1600:1700] + [2145:2185])",
            "(SR_B6 - SR_B7)/(SR_B6 + SR_B7)",
        ),
        ("(-485nm + 660nm)/660nm", "(-SR_B2 + SR_B4)/SR_B4"),
    ],
)
def test_landsat_formula(formula, expected_formula):
    assert convert_formula(formula, sat=landsat_bands) == expected_formula
