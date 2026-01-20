from utils.sat_spec_reader import parse_satellite_bands_table
from utils.formula_processing import convert_formula
import pandas as pd


def generate_excel_formulas(
    index_table_path: str,
    satellite_specification_path: str,
    output_path: str | None = "indicies.xlsx",
):
    """Генерирует формулы индексов для конкертных спутников"""
    df = pd.read_excel(index_table_path)
    satellites = parse_satellite_bands_table(satellite_specification_path)
    for sat in satellites:
        df[sat] = df["formula"].apply(
            lambda x: convert_formula(x, satellites[sat]))
    df.to_excel(output_path, index=False)
    return f"Файл сохранен в {index_table_path}"
