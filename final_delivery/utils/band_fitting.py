HYPERSPEC_BANDS_NUM = 50
IOU_TRESHOLD = 0.5


# ---Finding correct band---
def _hyperspec_to_band(wl_min: float, wl_max: float, bands: dict):
    center = (wl_min + wl_max)/2
    for band_name in bands:
        if bands[band_name][0] < center < bands[band_name][1]:
            return band_name
    return "no_suitable"


def _overlap_of_index(wl_min: float, wl_max: float, b_min, b_max: float):
    if (wl_min > b_max) or (wl_max < b_min):
        return None
    else:
        return (min(wl_max, b_max) - max(wl_min, b_min))/(wl_max-wl_min)


def _multuband_to_band(wl_min: float, wl_max: float, bands: dict):
    if wl_max == wl_min:
        return _hyperspec_to_band(wl_min, wl_max, bands)
    best_ooi = 0
    best_band_name = "no_suitable"
    for band_name in bands:
        ooi = _overlap_of_index(
            wl_min=wl_min,
            wl_max=wl_max,
            b_min=bands[band_name][0],
            b_max=bands[band_name][1]
        )
        if ooi is None:
            continue
        if ooi > best_ooi:
            best_ooi = ooi
            best_band_name = band_name
    return best_band_name


def wavelength_to_band(wl_min: float, wl_max: float, bands: dict) -> str:
    if len(bands) > HYPERSPEC_BANDS_NUM:
        band = _hyperspec_to_band(wl_min, wl_max, bands)
    else:
        band = _multuband_to_band(wl_min, wl_max, bands)
    return band
