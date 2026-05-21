import os

import polars as pl

INPUT_PATH = "data/interim/imputado.csv"
OUT_CSV = "data/processed/transformado.csv"


def transform_data(
    input_path: str,
    out_csv: str,
) -> None:
    """
    Calcula el promedio de notas, estado de aprobación y categoría académica.
    """
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    df = pl.read_csv(input_path)

    df_transformate = df.with_columns(
        pl.mean_horizontal(
            "nota1",
            "nota2",
            "nota3",
        )
        .round(2)
        .alias("promedio")
    ).with_columns(
        (pl.col("promedio") >= 4.0).alias("aprobado"),
        pl.when(pl.col("promedio") >= 6.0)
        .then(pl.lit("Destacado"))
        .when(pl.col("promedio") >= 4.0)
        .then(pl.lit("Aprobado"))
        .otherwise(pl.lit("Reprobado"))
        .alias("categoria"),
    )

    df_transformate.write_csv(out_csv)


if __name__ == "__main__":
    transform_data(
        INPUT_PATH,
        OUT_CSV,
    )
