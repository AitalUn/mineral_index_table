from formula_generator import generate_excel_formulas
from pathlib import Path

satellite_specification_path = Path(__file__).parent / "specification" / "Спутники.xlsx"
index_table_path = Path(__file__).parent / "specification" / "FilteredFormulas.xlsx"
output_path = Path(__file__).parent / "indicies.xlsx"

if __name__ == "__main__":
    generate_excel_formulas( 
        index_table_path=index_table_path,
        satellite_specification_path=satellite_specification_path,
        output_path=output_path
    )

