from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import TamborResult


OUTPUT_COLUMNS = ["NumeroTambor", "Resultado", "Estado", "Mensaje", "FechaHora"]


def _clean_tambor_value(value: object) -> str:
    if pd.isna(value):
        return ""

    if isinstance(value, float) and value.is_integer():
        return str(int(value))

    return str(value).strip()


def load_tambores(input_path: Path) -> list[str]:
    if not input_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo de entrada: {input_path}")

    dataframe = pd.read_excel(input_path, engine="openpyxl")
    if dataframe.empty:
        raise ValueError("El archivo Tambores.xlsx esta vacio.")

    column_name = "NumeroTambor" if "NumeroTambor" in dataframe.columns else dataframe.columns[0]
    values = [_clean_tambor_value(value) for value in dataframe[column_name].tolist()]
    tambores = [value for value in values if value]

    if not tambores:
        raise ValueError("No se encontraron numeros de tambor en la primera columna.")

    return tambores


def load_existing_results(output_path: Path) -> dict[str, TamborResult]:
    if not output_path.exists():
        return {}

    dataframe = pd.read_excel(output_path, engine="openpyxl")
    if dataframe.empty:
        return {}

    for column in OUTPUT_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = ""

    results: dict[str, TamborResult] = {}
    for row in dataframe[OUTPUT_COLUMNS].fillna("").to_dict("records"):
        numero = _clean_tambor_value(row["NumeroTambor"])
        if not numero:
            continue

        results[numero] = TamborResult(
            numero_tambor=numero,
            resultado=str(row["Resultado"]).strip(),
            estado=str(row["Estado"]).strip(),
            mensaje=str(row["Mensaje"]).strip(),
            fecha_hora=str(row["FechaHora"]).strip(),
        )

    return results


def save_results(output_path: Path, input_order: list[str], results: dict[str, TamborResult]) -> None:
    rows = []
    seen: set[str] = set()

    for numero in input_order:
        if numero in seen:
            continue
        seen.add(numero)

        result = results.get(numero)
        if result:
            rows.append(result.to_row())
        else:
            rows.append(
                {
                    "NumeroTambor": numero,
                    "Resultado": "",
                    "Estado": "",
                    "Mensaje": "",
                    "FechaHora": "",
                }
            )

    dataframe = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    tmp_path = output_path.with_suffix(".tmp.xlsx")
    dataframe.to_excel(tmp_path, index=False, engine="openpyxl")
    tmp_path.replace(output_path)
