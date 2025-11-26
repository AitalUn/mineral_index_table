import pandas as pd
from sympy import sympify, simplify
import sympy as sp
import re
from pathlib import Path


def parse_satellite_bands_table(
    data_path: Path,
) -> dict:
    ''''''
    satellite_data = pd.ExcelFile(data_path)
    satellite_bands = {}
    
    for sat in satellite_data.sheet_names:
        data = {}
        try:
            df = pd.read_excel(data_path ,sheet_name = sat)
            for a, d in zip(df['Алиас'],df['Диапазон, нм']):
                if type(a) != str:
                    continue
                bounds = [
                    round(float(d.split("-")[0]), 2),
                    round(float(d.split("-")[1]), 2)
                ]
                data[a] = bounds
        except:
            print(f"Не удалось спарсить лист: {sat}")
        satellite_bands[sat] = data
    return satellite_bands


def wavelength_to_band(wl_min: float, wl_max:float, bands:dict) -> str:
    '''Подбирает подходящий бэнд под диапазон'''
    for bname, (bmin, bmax) in bands.items():
        # intersection check
        if wl_min >= bmin and wl_max <= bmax:
            return bname
    return "nan"


def convert_formula(formula:str, sat:dict) -> str:
    '''Подставляем вместо диапаизона алиас канала для конкретного спутника'''
    f = formula
    # --- Replace ranges [700:710] ---
    def repl_range(m):
        lo = int(m.group(1))
        hi = int(m.group(2))
        b = wavelength_to_band(lo, hi, sat)
        return b

    f = re.sub(r"\[(\d+):(\d+)\]", repl_range, f)

    # --- Replace single [700] ---
    def repl_single(m):
        wl = int(m.group(1))
        b = wavelength_to_band(wl, wl, sat)
        return b

    f = re.sub(r"\[(\d+)\]", repl_single, f)

    # --- Replace "700nm" ---
    def repl_nm(m):
        wl = int(m.group(1))
        b = wavelength_to_band(wl, wl, sat)
        return b

    f = re.sub(r"(\d+)nm", repl_nm, f)
    # If variables like RED, BLUE appear — leave as is.

    # --- Simplify with sympy ---
    try:
        expr = sympify(f)
        simplified = simplify(expr)
        
        # Проверяем, является ли результат константой
        if simplified.is_constant():
            return "constant"
        elif 'zoo' in str(simplified):
            return "nan"
        else:
            f = str(simplified)
    except Exception:
        pass
    return f


def generate_excel_formulas(
    index_table_path: str,
    satellite_specification_path: str,
    output_path: str | None = "indicies.xlsx"
):
    '''Генерирует формулы индексов для конкертных спутников'''
    df = pd.read_excel(index_table_path)
    satellites = parse_satellite_bands_table(satellite_specification_path)
    for sat in satellites:
        df[sat] = df['formula'].apply(lambda x: convert_formula(x, satellites[sat]))
    df.to_excel(output_path, index=False)
    return f"Файл сохранен в {index_table_path}"