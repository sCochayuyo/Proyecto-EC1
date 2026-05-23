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

    df.with_columns(pl.any_horizontal(pl.all().is_null()).alias("tiene_faltantes")).write_csv(
        out_csv
    )

    nulls_per_column = df.select(pl.all().is_null().sum()).to_dicts()[0]

    df_missing = (
        df.with_row_index("fila", offset=1)
        .filter(pl.any_horizontal(pl.all().is_null()))
        .select(
            "fila",
            pl.concat_str(
                [
                    pl.when(pl.col(col).is_null()).then(pl.lit(col)).otherwise(pl.lit(""))
                    for col in df.columns
                ],
                separator=", ",
            )
            .str.replace_all(r"(, )+", ", ")
            .str.strip_chars(", ")
            .alias("detalle"),
        )
    )

    df_abnormal = (
        df.with_row_index("fila", offset=1)
        .with_columns(
            pl.concat_str(
                [
                    pl.when((pl.col(col) < 1.0) | (pl.col(col) > 7.0))
                    .then(pl.lit(f"{col} fuera de rango"))
                    .otherwise(pl.lit(""))
                    for col in [
                        "nota1",
                        "nota2",
                        "nota3",
                    ]
                ]
                + [
                    pl.when((pl.col("asistencia") < 0) | (pl.col("asistencia") > 100))
                    .then(pl.lit("asistencia fuera de rango"))
                    .otherwise(pl.lit(""))
                ],
                separator=", ",
            )
            .str.replace_all(r"(, )+", ", ")
            .str.strip_chars(", ")
            .alias("detalle")
        )
        .filter(pl.col("detalle").str.len_chars() > 0)
        .select("fila", "detalle")
    )

    str_missing = (
        "  Ninguno.\n"
        if df_missing.height == 0
        else df_missing.select(
            pl.concat_str(
                [
                    pl.lit("  - Fila "),
                    pl.col("fila"),
                    pl.lit(": "),
                    pl.col("detalle"),
                    pl.lit("\n"),
                ]
            )
            .implode()
            .list.join("")
        ).item()
    )

    str_abnormal = (
        "  Ninguna.\n"
        if df_abnormal.height == 0
        else df_abnormal.select(
            pl.concat_str(
                [
                    pl.lit("  - Fila "),
                    pl.col("fila"),
                    pl.lit(": "),
                    pl.col("detalle"),
                    pl.lit("\n"),
                ]
            )
            .implode()
            .list.join("")
        ).item()
    )

    report = (
        "Reporte de validación de estudiantes.csv\n"
        "----------------------------------------\n"
        f"Total de filas procesadas: {df.height}\n\n"
        "Valores faltantes por columna:\n"
        + "".join(f"  - {col}: {n}\n" for col, n in nulls_per_column.items())
        + "\nFilas con datos faltantes:\n"
        + str_missing
        + "\nValores fuera de rango:\n"
        + str_abnormal
    )

    with open(out_txt, "w", encoding="utf-8") as file:
        file.write(report)


if __name__ == "__main__":
    validate_data(
        INPUT_PATH,
        OUT_CSV,
        OUT_TXT,
    )
