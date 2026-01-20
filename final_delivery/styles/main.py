from coloring_v3 import generate_qml
from pathlib import Path

from tqdm import tqdm

# raster_path = Path(__file__).parent.parent / "new_chukotka" / "1_coged" 
raster_path = Path(r"D:\ml_datasets\Забайкалье\LANDSAT45_INDICES_coged") 


for f in tqdm(raster_path.iterdir()):
    generate_qml(
        raster_path=str(f),
        qml_path=str(f.with_suffix(".qml")),
        classes=5,
        invert=True
    )