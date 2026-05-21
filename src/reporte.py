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
    imputed_names = imputed_df["nombre"].to_list()
    total_imputed = len(imputed_names)

    if total_imputed > 0:
        name_str = ", ".join(imputed_names)
    else:
        name_str = "Ninguno"

    students_table_df = df.select(
        [
            "nombre",
            "nota1",
            "nota2",
            "nota3",
            "asistencia",
            "promedio",
            "aprobado",
            "categoria",
        ]
    )

    markdown_table = (
        "| Nombre | Nota 1 | Nota 2 | Nota 3 | "
        "Asistencia | Promedio | Aprobado | Categoria |\n"
        "| :--- | :---: | :---: | :---: | "
        ":---: | :---: | :---: | :--- |\n"
    )

    for row in students_table_df.iter_rows():
        passed_str = "Si" if row[6] else "No"
        markdown_table += (
            f"| {row[0]} | {row[1]} | {row[2]} | "
            f"{row[3]} | {row[4]}% | {row[5]:.2f} | "
            f"{passed_str} | {row[7]} |\n"
        )

    md_report = (
        "# Reporte final\n\n"
        f"**Fecha de generación:** {current_date}\n\n"
        "## 1. Tabla markdown con estudiantes y sus resultados\n\n"
        f"{markdown_table}\n\n"
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
