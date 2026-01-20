from utils.band_fitting import wavelength_to_band

from sympy import sympify, simplify
from sympy.core.sympify import SympifyError
import re


# --- Replace ranges [700:710] ---
def _repl_range(match, sat):
    lo = int(match.group(1))
    hi = int(match.group(2))
    return wavelength_to_band(lo, hi, sat)


# --- Replace single [700] ---
def _repl_single(match, sat):
    wl = int(match.group(1))
    return wavelength_to_band(wl, wl, sat)


# --- Replace "700nm" ---
def _repl_nm(match, sat):
    wl = int(match.group(1))
    return wavelength_to_band(wl, wl, sat)


def _make_sympy_formula(formula):
    expr = sympify(formula)
    return simplify(expr)


def convert_formula(formula: str, sat: dict) -> str:
    formula = re.sub(r"\[(\d+):(\d+)\]", lambda match: _repl_range(match, sat), formula)
    formula = re.sub(r"\[(\d+)\]", lambda match: _repl_single(match, sat), formula)
    formula = re.sub(r"(\d+)nm", lambda match: _repl_nm(match, sat), formula)
    # --- Simplify with sympy ---

    if "no_suitable" in formula:
        return "nan"

    try:
        simplified = _make_sympy_formula(formula)
    except:
        return "Error in formula"

    if simplified.is_constant():
        return "constant"
    elif "zoo" in str(simplified):
        return "nan"
    else:
        return str(simplified)
