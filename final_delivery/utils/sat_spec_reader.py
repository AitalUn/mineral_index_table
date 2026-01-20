from pathlib import Path
import pandas as pd


# ---Reading satellite data---
def _parse_sinle_satellite(sat_df, sat):
    current_sat_data = {}
    for alias, range in zip(sat_df['Алиас'], sat_df['Диапазон, нм']):
        if not isinstance(alias, str):
            continue
        current_sat_data[alias] = [
                round(float(range.split("-")[0]), 2),
                round(float(range.split("-")[1]), 2),
            ]
    return current_sat_data


def parse_satellite_bands_table(
    data_path: Path,
) -> dict:

    sat_data = pd.ExcelFile(data_path)
    sat_bands_range = {}
    for sat in sat_data.sheet_names:
        sat_df = pd.read_excel(data_path, sheet_name=sat)
        if "Алиас" not in sat_df.columns:
            continue
        sat_bands_range[sat] = _parse_sinle_satellite(sat_df, sat)

    return sat_bands_range
