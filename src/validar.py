import os

import polars as pl

INPUT_PATH = "data/raw/estudiantes.csv"
OUT_CSV = "data/interim/validado.csv"
OUT_TXT = "data/interim/reporte_validacion.txt"


def validate_data(
    input_path: str,
    out_csv: str,
    out_txt: str,
) -> None:
    """
    Procesa el dataset de estudiantes para identificar datos faltantes
    generando un nuevo dataset y un reporte.
    """
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    os.makedirs(os.path.dirname(out_txt), exist_ok=True)

    df = pl.read_csv(input_path)

    original_columns = df.columns

    df_validated = df.with_columns(
        pl.any_horizontal(
            pl.all().is_null(),
        ).alias("tiene_faltantes")
    )

    df_validated.write_csv(out_csv)

    total_rows = df.height

    nulls_per_columns = df.select(pl.all().is_null().sum()).to_dicts()[0]

    df_indexed = df.with_row_index("fila", offset=1)

    rows_with_nulls_df = df_indexed.filter(df_validated["tiene_faltantes"])
    rows_with_nulls = rows_with_nulls_df.height

    invalid_rows = []

    for row in df_indexed.iter_rows(named=True):
        errors = []
        grade_columns = ["nota1", "nota2", "nota3"]

        for grade_col in grade_columns:
            value = row.get(grade_col)
            if value is not None and (value < 1.0 or value > 7.0):
                errors.append(f"{grade_col} Fuera de rango (Dato anomalo): {value}")

        attendace_value = row.get("asistencia")
        if attendace_value is not None and (attendace_value < 0 or attendace_value > 100):
            errors.append(f"Asistencia fuera de rango (Dato anomalo): {attendace_value}")

        if errors:
            invalid_rows.append(f"Fila {row['row_num']}: " + ", ".join(errors))

    report = (
        "Reporte de validación de estudiantes.csv\n"
        "----------------------------------------\n"
        f"Total de filas procesadas: {total_rows}\n\n"
        "Valores faltantes por columna:\n"
    )

    for column, null_count in nulls_per_columns.items():
        report += f"- {column}: {null_count}\n"

    report += "\nFilas con al menos un dato faltante:\n"

    if rows_with_nulls > 0:
        for row in rows_with_nulls_df.iter_rows(named=True):
            missing_columns = []

            for column in original_columns:
                if row.get(column) is None:
                    missing_columns.append(column)

            report += f"- Fila {row['fila']}: " + ", ".join(missing_columns) + "\n"
    else:
        report += "No se encontraron filas con faltantes.\n"

    report += "\nValores fuera de rango (Datos anomalos):\n"

    if invalid_rows:
        for error in invalid_rows:
            report += f"- {error}\n"
    else:
        report += "No se encontraron valores fuera de rango.\n"

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    validate_data(
        INPUT_PATH,
        OUT_CSV,
        OUT_TXT,
    )
