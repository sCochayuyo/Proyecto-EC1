from datetime import datetime
import os

import polars as pl

CSV_PATH = "data/processed/transformado.csv"
TXT_PATH = "data/processed/resumen.txt"
OUT_MD = "reports/reporte_final.md"


def generate_report(
    csv_path: str,
    txt_path: str,
    out_md: str,
) -> None:
    """
    Generación de reporte final en formato Markdown con metricas y tabla
    """
    os.makedirs(os.path.dirname(out_md), exist_ok=True)

    df = pl.read_csv(csv_path)

    with open(txt_path, "r", encoding="utf-8") as archive:
        resume_txt = archive.read()

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    imputed_df = df.filter(pl.col("tiene_faltantes"))
    total_imputed = imputed_df.height

    if total_imputed > 0:
        name_str = imputed_df.select(pl.col("nombre").implode().list.join(", ")).item()
    else:
        name_str = "Ninguno"

    markdown_table = (
        "| Nombre | Nota 1 | Nota 2 | Nota 3 | "
        "Asistencia | Promedio | Aprobado | Categoria |\n"
        "| :--- | :---: | :---: | :---: | "
        ":---: | :---: | :---: | :--- |\n"
    )

    df_markdown = df.with_columns(
        pl.concat_str(
            [
                pl.lit("| "),
                pl.col("nombre"),
                pl.lit(" | "),
                pl.col("nota1"),
                pl.lit(" | "),
                pl.col("nota2"),
                pl.lit(" | "),
                pl.col("nota3"),
                pl.lit(" | "),
                pl.col("asistencia").cast(pl.String),
                pl.lit("% | "),
                pl.col("promedio").round(2).cast(pl.String),
                pl.lit(" | "),
                pl.col("aprobado").cast(pl.String),
                pl.lit(" | "),
                pl.col("categoria"),
                pl.lit(" |\n"),
            ]
        ).alias("md_row")
    )

    markdown_body = (
        df_markdown.select(pl.col("md_row").implode().list.join("")).item()
        if df_markdown.height > 0
        else ""
    )

    markdown = markdown_table + markdown_body

    md_report = (
        "# Reporte final\n\n"
        f"**Fecha de generación:** {current_date}\n\n"
        "## 1. Tabla markdown con estudiantes y sus resultados\n\n"
        f"{markdown}\n\n"
        "## 2. Contenido íntegro del resumen estadístico\n\n"
        f"{resume_txt}\n\n"
        "## 3. Observaciones sobre datos imputados\n\n"
        f"- **Cantidad de estudiantes con registros "
        f"imputados:** {total_imputed}\n"
        f"- **Estudiantes afectados:** {name_str}\n\n"
    )

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md_report)


if __name__ == "__main__":
    generate_report(
        CSV_PATH,
        TXT_PATH,
        OUT_MD,
    )
