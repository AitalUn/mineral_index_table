import pandas as pd
from sympy import sympify, simplify
import re
from pathlib import Path


def parse_satellite_bands_table(
    data_path: Path,
) -> dict:
    """"""
    satellite_data = pd.ExcelFile(data_path)
    satellite_bands = {}

    for sat in satellite_data.sheet_names:
        data = {}
        df = pd.read_excel(data_path, sheet_name=sat)
        if "Алиас" not in df.columns:
            continue
        try:
            for a, d in zip(df["Алиас"], df["Диапазон, нм"]):
                if type(a) is not str:
                    continue
                bounds = [
                    round(float(d.split("-")[0]), 2),
                    round(float(d.split("-")[1]), 2),
                ]
                data[a] = bounds
        except Exception: 
            print(f"Не удалось спарсить лист: {sat}")
        satellite_bands[sat] = data
    return satellite_bands


def wavelength_to_band(wl_min: float, wl_max: float, bands: dict) -> str:
    is_hyperspec = len(bands) > 100

    # convert bands dict to list of tuples: (name, bmin, bmax)
    band_list = [(bname, b[0], b[1]) for bname, b in bands.items()]

    # --- CASE 1: single wavelength ---
    if wl_min == wl_max:
        wl = wl_min

        # hyperspectral: pick band containing wl (or closest)
        if is_hyperspec:
            best = None
            best_dist = float("inf")
            for bname, bmin, bmax in band_list:
                if bmin <= wl <= bmax:
                    return bname
                # compute distance to band center
                center = (bmin + bmax) / 2
                dist = abs(center - wl)
                if dist < best_dist:
                    best_dist = dist
                    best = bname
            return best if best else "nan"

        # multispectral
        for bname, bmin, bmax in band_list:
            if bmin <= wl <= bmax:
                return bname
        return "nan"

    # --- CASE 2: range ---
    W = wl_max - wl_min

    # hyperspectral: pick band at the midpoint
    if is_hyperspec:
        mid = (wl_min + wl_max) / 2
        best = None
        best_dist = float("inf")
        for bname, bmin, bmax in band_list:
            center = (bmin + bmax) / 2
            dist = abs(center - mid)
            if dist < best_dist:
                best_dist = dist
                best = bname
        return best if best else "nan"

    # multispectral: intersection ≥ 50%
    best = None
    best_overlap = 0

    for bname, bmin, bmax in band_list:
        intersection = min(bmax, wl_max) - max(bmin, wl_min)
        if intersection <= 0:
            continue
        if intersection >= 0.5 * W:
            if intersection > best_overlap:
                best_overlap = intersection
                best = bname

    return best if best else "nan"


def convert_formula(formula: str, sat: dict) -> str:
    f = formula
    has_nan = False  # флаг что какой-то диапазон не покрывается

    # --- Replace ranges [700:710] ---
    def repl_range(m):
        nonlocal has_nan
        lo = int(m.group(1))
        hi = int(m.group(2))
        b = wavelength_to_band(lo, hi, sat)
        if b == "nan":
            has_nan = True
            return "nan"
        return b

    f = re.sub(r"\[(\d+):(\d+)\]", repl_range, f)

    # --- Replace single [700] ---
    def repl_single(m):
        nonlocal has_nan
        wl = int(m.group(1))
        b = wavelength_to_band(wl, wl, sat)
        if b == "nan":
            has_nan = True
            return "nan"
        return b

    f = re.sub(r"\[(\d+)\]", repl_single, f)

    # --- Replace "700nm" ---
    def repl_nm(m):
        nonlocal has_nan
        wl = int(m.group(1))
        b = wavelength_to_band(wl, wl, sat)
        if b == "nan":
            has_nan = True
            return "nan"
        return b

    f = re.sub(r"(\d+)nm", repl_nm, f)

    # Если что-то не покрылось — сразу "nan"
    if has_nan:
        return "nan"

    # --- Simplify with sympy ---
    try:
        expr = sympify(f)
        simplified = simplify(expr)

        if simplified.is_constant():
            return "constant"
        elif "zoo" in str(simplified):
            return "nan"
        else:
            return str(simplified)
    except Exception:
        return f


def generate_excel_formulas(
    index_table_path: str,
    satellite_specification_path: str,
    output_path: str | None = "indicies.xlsx",
):
    """Генерирует формулы индексов для конкертных спутников"""
    df = pd.read_excel(index_table_path)
    satellites = parse_satellite_bands_table(satellite_specification_path)
    for sat in satellites:
        df[sat] = df["formula"].apply(lambda x: convert_formula(x, satellites[sat]))
    df.to_excel(output_path, index=False)
    return f"Файл сохранен в {index_table_path}"
