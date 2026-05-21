import os

import polars as pl

INPUT_PATH = "data/interim/validado.csv"
OUT_CSV = "data/interim/imputado.csv"


def impute_data(
    input_path: str,
    out_csv: str,
) -> None:
    """
    Imputa los valores numéricos faltantes en el dataset aplicando:
    - Notas: imputación con la mediana de la columna.
    - Asistencia: imputación con la media de la columna.
    """
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    df = pl.read_csv(input_path)

    df_impute = df.with_columns(
        [
            pl.col("nota1").fill_null(
                pl.col("nota1").median(),
            ),
            pl.col("nota2").fill_null(
                pl.col("nota2").median(),
            ),
            pl.col("nota3").fill_null(
                pl.col("nota3").median(),
            ),
            pl.col("asistencia").fill_null(
                pl.col("asistencia").mean().round(0),
            ),
        ],
    )

    df_impute.write_csv(out_csv)


if __name__ == "__main__":
    impute_data(
        INPUT_PATH,
        OUT_CSV,
    )
