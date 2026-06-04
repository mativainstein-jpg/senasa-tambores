from pathlib import Path

import pandas as pd


output_path = Path(__file__).resolve().parent / "Tambores.xlsx"
dataframe = pd.DataFrame({"NumeroTambor": [""]})
dataframe.to_excel(output_path, index=False, engine="openpyxl")
print(f"Plantilla creada: {output_path}")
