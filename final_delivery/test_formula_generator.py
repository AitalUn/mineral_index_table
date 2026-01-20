import pytest
from pathlib import Path
from utils.formula_processing import convert_formula
from utils.sat_spec_reader import parse_satellite_bands_table

SPEC_PATH = Path(__file__).parent / "specification" / "Спутники.xlsx"
FORMULAS = ["[2145:2185]/[2185:2225]", "800nm/635nm", "1660nm/550nm"]

@pytest.fixture
def bands():
    return parse_satellite_bands_table(SPEC_PATH)

@pytest.mark.parametrize("satellite,expected", [
    ("ASTER", ["B5/B6", "B3N/B2", "B4/B1"]),
    ("LANDSAT-89 OLITIRS", ["constant", "nan", "nan"]),
])
def test_all_formulas(bands, satellite, expected):
    """Проверяет все формулы для указанного спутника."""
    for formula, exp in zip(FORMULAS, expected):
        result = convert_formula(formula, bands[satellite])
        assert result == exp, f"{satellite}: {formula}"