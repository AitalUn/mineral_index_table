import rasterio
import numpy as np
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def rgb_to_hex(rgb_str):
    """Конвертируем 'R,G,B,A' в '#RRGGBB'"""
    r, g, b, *_ = map(int, rgb_str.split(","))
    return f"#{r:02x}{g:02x}{b:02x}"

def generate_qml(
    raster_path,
    qml_path,
    classes=5,
    invert=True
):
    # ---------- READ DATA ----------
    with rasterio.open(raster_path) as src:
        data = src.read(1).astype("float64")
        if src.nodata is not None:
            data[data == src.nodata] = np.nan
        data = data[np.isfinite(data)]

    if data.size == 0:
        raise ValueError("Нет валидных данных")

    mu = float(data.mean())
    sigma = float(data.std())

    vmin = mu - 3 * sigma
    vmax = mu + 3 * sigma

    # ---------- EQUAL INTERVALS ----------
    values = np.linspace(vmin, vmax, classes)

    # ---------- SPECTRAL (QGIS-like) ----------
    spectral = [
        "215,25,28,255",
        "253,174,97,255",
        "255,255,191,255",
        "171,221,164,255",
        "43,131,186,255",
    ]

    if invert:
        spectral = list(reversed(spectral))

    if classes != 5:
        idx = np.linspace(0, len(spectral) - 1, classes).astype(int)
        spectral = [spectral[i] for i in idx]

    # ---------- QML ----------
    root = Element(
        "qgis",
        version="3.40.8-Bratislava",
        styleCategories="Symbology"
    )

    pipe = SubElement(root, "pipe")

    renderer = SubElement(
        pipe,
        "rasterrenderer",
        type="singlebandpseudocolor",
        band="1",
        classificationMin=str(vmin),
        classificationMax=str(vmax),
        opacity="1",
        alphaBand="-1"
    )

    minmax = SubElement(renderer, "minMaxOrigin")
    SubElement(minmax, "limits").text = "None"
    SubElement(minmax, "extent").text = "WholeRaster"
    SubElement(minmax, "statAccuracy").text = "Estimated"
    SubElement(minmax, "cumulativeCutLower").text = "0.02"
    SubElement(minmax, "cumulativeCutUpper").text = "0.98"
    SubElement(minmax, "stdDevFactor").text = "2"

    shader = SubElement(renderer, "rastershader")

    crs = SubElement(
        shader,
        "colorrampshader",
        colorRampType="INTERPOLATED",
        classificationMode="2",  # Equal Interval
        minimumValue=str(vmin),
        maximumValue=str(vmax),
        clip="0",
        labelPrecision="4"
    )

    # ----- COLOR RAMP -----
    ramp = SubElement(crs, "colorramp", type="gradient", name="[source]")
    opt = SubElement(ramp, "Option", type="Map")
    SubElement(opt, "Option", name="color1", type="QString", value=rgb_to_hex(spectral[0]))
    SubElement(opt, "Option", name="color2", type="QString", value=rgb_to_hex(spectral[-1]))
    SubElement(opt, "Option", name="discrete", type="QString", value="0")
    SubElement(opt, "Option", name="rampType", type="QString", value="gradient")
    SubElement(opt, "Option", name="spec", type="QString", value="rgb")

    # ----- ITEMS -----
    for v, c in zip(values, spectral):
        SubElement(
            crs,
            "item",
            value=f"{v:.6f}",
            color=rgb_to_hex(c),
            label=f"{v:.4f}",
            alpha="255"
        )

    # ---------- SAVE ----------
    xml = minidom.parseString(tostring(root))
    with open(qml_path, "w", encoding="utf-8") as f:
        f.write(xml.toprettyxml(indent="  "))

    print("✅ QML СГЕНЕРИРОВАН И БУДЕТ РИСОВАТЬ")
    print(f"μ = {mu:.5f}")
    print(f"σ = {sigma:.5f}")
    print(f"range = [{vmin:.5f}, {vmax:.5f}]")
    print(f"classes = {classes}")

# ===== TEST =====
# generate_qml(
#     r"D:\ml_datasets\Забайкалье\landsat45_PCA\clay.tif",
#     r"D:\ml_datasets\Забайкалье\landsat45_PCA\clay.qml",
#     classes=5,
#     invert=True
# )
# ========== COLORING_V3.PY ==========